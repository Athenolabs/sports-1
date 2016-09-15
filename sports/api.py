import frappe
from frappe import _
from frappe.utils import nowdate, add_days
from time import gmtime, strftime
from operator import itemgetter
from frappe.utils.background_jobs import enqueue


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
def update_standings(event):
	event = frappe.get_doc("Game Event", event)
	game = frappe.get_doc("Game", event.game)
	season = frappe.get_doc("Season", game.season)
	now = strftime("%Y-%m-%d %H:%M:%S", gmtime())

	standings = []
	for team in season.teams:
		team_games_as_host = frappe.db.sql("SELECT * FROM tabGame WHERE season='%s' AND host_team='%s' AND status='Played' " % (season.title,team.team), as_dict=1)
		team_games_as_guest = frappe.db.sql("SELECT * FROM tabGame WHERE season='%s' AND guest_team='%s' AND status='Played'" % (season.title,team.team), as_dict=1)

			
		host_stats = get_stats(team, team_games_as_host)
		guest_stats = get_stats(team, team_games_as_guest)


		standing = {
			"doctype":"Team Standing",
			"team":team.team,
			"games": len(team_games_as_host)+len(team_games_as_guest),
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
	standings = sorted(standings, key=itemgetter('points'), reverse=True)
	for position, standing in enumerate(standings):
		standing['position'] = position + 1
		season.append("team_standings", standing)
	season.last_standings_update = now
	season.save()
	frappe.db.commit()


def update_standings_after_event(doc, method):
	enqueue(update_standings,event="e03ce9b20e")

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