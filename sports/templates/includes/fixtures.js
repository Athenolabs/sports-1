fixtures = function(page) {

frappe.call({
                        method:"sports.api.get_season_fixtures",
                        args: {
                                season: "AZAM National Soccer League 2015-2016"
                        },
                        callback: function(data){
				fixtures = data.message;
				fixtures.forEach(function(fixture) {
					$('#fixtures-table tbody').append('<tr class="child"><td>'+fixture['day']+'</td><td>'+fixture['date']+'</td><td>'+fixture['host_team']+'</td><td>'+fixture['score']+'</td><td>'+fixture['guest_team']+'</td><td>'+fixture['venue']+'</td></tr>');
				});
                        }
                });




}
