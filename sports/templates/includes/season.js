standings = function(page) {

		var season = get_url_arg('season');
		var day = get_url_arg('day');
		frappe.call({
                        method:"sports.api.get_season_standings",
                        args: {
                                season: season
                        },
                        callback: function(data){
				standings = data.message;
				standings.forEach(function(standing) {
					$('#standings-table tbody').append(`
						<tr class="child">
							<td>${standing['position']}</td>
							<td><a href='/team?team=${standing['team']}'>${standing['team']}</a></td>
							<td>${standing['games']}</td>
							<td>${standing['wins']}</td>
							<td>${standing['losses']}</td>
							<td>${standing['draws']}</td>
							<td>${standing['goals_diff']}</td>
							<td>${standing['points']}</td>
						</tr>`);
				});
                        }
                });

                frappe.call({
                        method:"sports.api.get_player_standings",
                        args: {
                                season: season
                        },
                        callback: function(data){
                                standings = data.message;
                                standings.forEach(function(standing) {
                                        $('#scorers-table tbody').append(`
                                                <tr class="child">
                                                        <td><a href='/player?player=${standing['player']}'>${standing['player']}</a></td>
                                                        <td><a href='/team?team=${standing['team']}'>${standing['team']}</a></td>
                                                        <td>${standing['goals']}</td>
                                                </tr>`);
                                });
                        }
                });


		frappe.call({
                        method:"sports.api.get_season_fixtures",
                        args: {
                                season: season,
				day: day
                        },
                        callback: function(data){
				for(var i = 1; i <= 15; i++)
				{
					if(i == day)
						$("#days").append('<li class="active"><a href="/season?season='+season+'&day='+i+'">'+i+'</a></li>');
					else
						$("#days").append('<li><a href="/season?season='+season+'&day='+i+'">'+i+'</a></li>');
				}
                                fixtures = data.message;
                                fixtures.forEach(function(fixture) {
                                        $('#fixtures-table tbody').append('<tr class="child"><td>'+fixture['date']+'</td><td>'+fixture['host_team']+'</td><td>'+fixture['score']+'</td><td>'+fixture['guest_team']+'</td><td><a href="#">'+fixture['venue']+'</a></td></tr>');
                                });
                        }
                });


}
