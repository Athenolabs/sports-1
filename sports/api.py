import frappe
from frappe import _
from frappe.utils import nowdate, add_days
from time import gmtime, strftime
from operator import itemgetter
from frappe.utils.background_jobs import enqueue


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
	standings = frappe.get_list("Team Standing", filters=filters, fields=['name', 'team','games','wins', 'draws', 'losses', 'position', 'goals_diff','points'])
	return standings

def get_last_event(season):
	try:
    		return frappe.get_all("Game Event", filters={'season':season}, limit_page_length = 1)[0]["name"]
	except:
		return None

def update_standings_after_event(doc, method):
	update_standings(doc.name)

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
	standings = multikeysort(standings, ['-points','games','-goals_diff','goals_lost','team'])
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
