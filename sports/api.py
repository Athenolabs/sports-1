import frappe
from frappe import _
from frappe.utils import nowdate, add_days
from time import gmtime, strftime
from operator import itemgetter
from frappe.utils.background_jobs import enqueue
import facebook
import tweepy



@frappe.whitelist(allow_guest=True)
def get_menu(season):
	countries = frappe.get_list("Country Sport", fields=['country', 'sport'])
	return countries

@frappe.whitelist(allow_guest=True)
def get_sports(country):
	sports = frappe.get_list("Country Sport", filters={'country':country},fields=['country', 'sport'])
	return sports

@frappe.whitelist(allow_guest=True)
def get_seasons(tournament):
	seasons = frappe.get_list("Season", filters={'tournament':tournament},fields=['name'])
	return seasons

@frappe.whitelist(allow_guest=True)
def get_current_season(tournament):
	seasons = frappe.get_list("Season", filters={'tournament':tournament},fields=['name'])
	return seasons[0]

@frappe.whitelist(allow_guest=True)
def get_seasons_archives(tournament):
	seasons = frappe.get_list("Season", filters={'tournament':tournament},fields=['name'])
	return seasons[1:]

@frappe.whitelist(allow_guest=True)
def get_season_fixtures(season, day=1):
	fixtures = frappe.get_list("Game", filters={'season':season, 'day':day}, fields=['day', 'date','host_team','score', 'guest_team', 'venue', 'name'], order_by="day, date")
	return fixtures


@frappe.whitelist(allow_guest=True)
def get_season_standings(season):
	filters = {'season':season}
	last_event = get_last_event(season)
	if last_event:
		filters['event'] = last_event
	standings = frappe.get_list("Team Standing", filters=filters, fields=['name', 'team','games','wins', 'draws', 'losses', 'position', 'goals_won', 'goals_lost','goals_diff','points'], order_by="points desc, goals_diff desc, goals_won desc, team asc")
	return standings

@frappe.whitelist(allow_guest=True)
def get_player_standings(season):
	filters = {'season':season}
	last_event = get_last_event(season)
	if last_event:
		filters['event'] = last_event
	standings = frappe.get_list("Player Standing", filters=filters, fields=['player', 'team','goals', 'season'], order_by="goals desc")
	return standings

def get_last_event(season):
	try:
    		return frappe.get_all("Game Event", filters={'season':season}, limit_page_length = 1)[0]["name"]
	except:
		return None


def update_standings_after_event(doc, method):
	event = frappe.get_doc("Game Event", doc.name)
	start_stop_game(event)
	enqueue(update_game_score, game_event=doc.name)
	enqueue(update_standings, game_event=doc.name)

def send_notifications(doc, method):
	event = frappe.get_doc("Game Event", doc.name)
	send_facebook(event)
	send_tweeter(event)

def send_facebook(event):
	  cfg = {
	    "page_id"      : "340556576293232",  # Step 1
	    "access_token" : "EAADstR7dElkBAM3lmprKwP3VCDcqNRHdPmYJTJJlhdcl4X5W4R6bm2jv8rWdanMm9egodipHDWmpIniCiZCylaGKphYdjZBVoy3v1ZB42RLSRnqawLzftQ5xzoDKX9HtCuvT98oZC2V8DL8k9wZAKhgicxUPZAfeIZD"   # Step 3
	    }

	  api = get_facebook_api(cfg)
	  msg = event.type
	  status = api.put_wall_post(msg)

def get_facebook_api(cfg):
	  graph = facebook.GraphAPI(cfg['access_token'])
	  resp = graph.get_object('me/accounts')
	  page_access_token = None
	  for page in resp['data']:
	    if page['id'] == cfg['page_id']:
	      page_access_token = page['access_token']
	  graph = facebook.GraphAPI(page_access_token)
	  return graph


def send_tweeter(event):
	  cfg = {
	    "consumer_key"        : "E6DpIXVSLj9rptOPWnIPqUgGL",
	    "consumer_secret"     : "iDS3XCM7MrUdpZRoqsPyHTpcbiF2Eiy0UVMC3suzeWk8LGiBbw",
	    "access_token"        : "779820333268426752-ccD1tQGnHKvtDMyJeCM2C9r35Uvf3mt",
	    "access_token_secret" : "8Ocu6BJahsXGfOKyjnNG3Tmk6S6l08onDS59IVRjgLhLD"
	  }
	  api = get_tweeter_api(cfg)
	  tweet = event.type
	  status = api.update_status(status=tweet) 
	  # Yes, tweet is called 'status' rather confusing

def get_tweeter_api(cfg):
	  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
	  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
	  return tweepy.API(auth)

def get_stats(team, games):
	stats = {
		'goals_won': 0,
		'goals_lost': 0,
		'wins': 0,
		'losses': 0,
		'draws': 0
	}

	for game in games:
		this_game = frappe.get_doc("Game", game['name'])
		goals = frappe.db.count("Game Event", filters={"game": game['name'], 'type':'Goal'})
		goals_won = frappe.db.count("Game Event", filters={"game": game['name'], "team":team.team, 'type':'Goal'})
		goals_lost = goals - goals_won
			
		if goals_won > goals_lost:
			stats['wins'] += 1
		if goals_won < goals_lost:
			stats['losses'] += 1
		elif goals_won == goals_lost:
			stats['draws'] += 1
		stats['goals_won'] += goals_won
		stats['goals_lost'] += goals_lost
	return stats
			
@frappe.whitelist()
def update_game_score(game_event):
	event = frappe.get_doc("Game Event", game_event)
	game = frappe.get_doc("Game", event.game)
	game.update_score()

def start_stop_game(event):
	game = frappe.get_doc("Game", event.game)
	if event.type == "Kick Off":
		game.kick_off()
	elif event.type == "End":
		game.end()

	
@frappe.whitelist()
def update_player_standings(game_event):
	event = frappe.get_doc("Game Event", game_event)
	game = frappe.get_doc("Game", event.game)
	season = frappe.get_doc("Season", game.season)
	now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	events = frappe.db.sql("SELECT COUNT(name) score, team,player FROM `tabGame Event` WHERE type='Goal' GROUP BY player ORDER BY score DESC, player;", as_dict=1)
	for event in events:
		new_standing = frappe.get_doc({
			"doctype":"Player Standing",
			"player":event["player"],
			"team":event["team"],
			"season":game.season,
			"goals":event["score"],
			"event":game_event
		})
		new_standing.insert()

@frappe.whitelist()
def update_standings(game_event):
	event = frappe.get_doc("Game Event", game_event)
	game = frappe.get_doc("Game", event.game)
	season = frappe.get_doc("Season", game.season)
	now = strftime("%Y-%m-%d %H:%M:%S", gmtime())

	standings = []
	for team in season.teams:
		team_games_as_host = frappe.db.sql("SELECT * FROM tabGame WHERE season='%s' AND host_team='%s' AND (status='Playing'  OR status='Played')" % (season.title,team.team), as_dict=1)
		team_games_as_guest = frappe.db.sql("SELECT * FROM tabGame WHERE season='%s' AND guest_team='%s' AND (status='Playing' OR status='Played')" % (season.title,team.team), as_dict=1)

			
		host_stats = get_stats(team, team_games_as_host)
		guest_stats = get_stats(team, team_games_as_guest)


		standing = {
			"doctype":"Team Standing",
			"team":team.team.upper(),
			"games": len(team_games_as_host)+len(team_games_as_guest),
			"season": game.season,
			"host_goals_won": host_stats['goals_won'],
			"host_goals_lost": host_stats['goals_lost'],
			"host_wins":host_stats['wins'],
			"host_draws":host_stats['draws'],
			"host_losses":host_stats['losses'],
			"guest_goals_won": guest_stats['goals_won'],
			"guest_goals_lost": guest_stats['goals_lost'],
			"guest_wins":guest_stats['wins'],
			"guest_draws":guest_stats['draws'],
			"guest_losses":guest_stats['losses'],
			"goals_won": host_stats['goals_won'] + guest_stats['goals_won'],
			"goals_lost": host_stats['goals_lost'] + guest_stats['goals_lost'],
			"wins":host_stats['wins'] + guest_stats['wins'],
			"draws":host_stats['draws'] + guest_stats['draws'],
			"losses":host_stats['losses'] + guest_stats['losses'],
			"event":event.name if event else None,
			"change":0
		}
		standing['points'] = standing['wins'] * 3 + standing['draws']
		standing['goals_diff'] = standing['goals_won'] - standing['goals_lost']
		standings.append(standing)
	#standings = sorted(standings, key=itemgetter('points'), reverse=True)
	standings = multikeysort(standings, ['-points','-goals_diff','-goals_won', 'team'])
	for position, standing in enumerate(standings):
		standing['position'] = position + 1
		new_standing = frappe.get_doc(standing)
		new_standing.insert()
	season.last_standings_update = now
	season.save()
	frappe.db.commit()

def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else
                  (itemgetter(col.strip()), 1)) for col in columns]
    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)

@frappe.whitelist()
def enrol_teams(season):
	season = frappe.get_doc("Season", season)
	season.teams = None
	season.save()
	teams = frappe.get_all("Team", filters={'division':1})
	for team in teams:
		season_team = {
			"doctype": "Season Team",
			"team":team.name
		}
		season.append("teams",season_team)
	season.save()


@frappe.whitelist()
def load_lineups(game, team):
	game = frappe.get_doc("Game", game)
	if not game.host_lineups:
		if team == "host":
			players = frappe.get_all("Player", filters={'team':game.host_team})
			for player in players:
				lineup = {
					"doctype": "Game Lineup",
					"team":game.host_team,
					"player":player.name
				}
				game.append("host_lineups",lineup)
		elif team == "guest":
			players = frappe.get_all("Player", filters={'team':game.guest_team})
			for player in players:
				lineup = {
					"doctype": "Game Lineup",
					"team":game.guest_team,
					"player":player.name
				}
				game.append("guest_lineups",lineup)

		game.save()

@frappe.whitelist()
def reset_lineups(game, team):
	game = frappe.get_doc("Game", game)
	if team == "host":
		game.host_lineups = None
	elif team == "guest":
		game.guest_lineups = None
	game.save()
