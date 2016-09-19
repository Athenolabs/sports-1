standings = function(page) {

		var season = get_url_arg('season');

		frappe.call({
                        method:"sports.api.get_season_standings",
                        args: {
                                season: season
                        },
                        callback: function(data){
				standings = data.message;
				standings.forEach(function(standing) {
					$('#standings-table tbody').append('<tr class="child"><td>'+standing['position']+'</td><td>'+standing['team']+'</td><td>'+standing['games']+'</td><td>'+standing['wins']+'</td><td>'+standing['losses']+'</td><td>'+standing['draws']+'</td><td>'+standing['points']+'</td><td>'+standing['last_1']+'</td><td>'+standing['last_2']+'</td><td>'+standing['last_3']+'</td><td>'+standing['last_4']+'</td><td>'+standing['last_5']+'</td></tr>');
				});
                        }
                });




}