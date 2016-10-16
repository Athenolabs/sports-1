menu = function(page) {
		frappe.call({
                        method:"sports.api.get_current_season",
                        args: {
                                tournament: "Rwanda National Football League"
                        },
                        callback: function(data){
                                season = data.message;
                        	$("#current-season").text(season['name']);
				$("#current-season").attr("href", '/season?season='+season['name'])

                        }
                });

		frappe.call({
                        method:"sports.api.get_seasons_archives",
                        args: {
                                tournament: "Rwanda National Football League"
                        },
                        callback: function(data){
                                seasons = data.message;
                                seasons.forEach(function(season) {
                                        $("#seasons-menu").append('<li><a href="/season?season='+season['name']+'">'+season['name']+'</a></li>');

                                });
                        }
                });

		frappe.call({
                        method:"sports.api.get_menu",
                        args: {
                                season: "AZAM National Soccer League 2015-2016"
                        },
                        callback: function(data){
				countries = data.message;
				countries.forEach(function(country) {
					$("#countries-menu").append('<li id="'+country['country']+'"><a href="#">'+country['country']+'</a></li>');

				});
                        }
                });


		/*
		$('li').off('click').on('click', function(event) {
			country = $(this).attr("id");

			alert(country)


			frappe.call({
				method:"sports.api.get_sports",
				args: {
					country: country[1]
				},
				callback: function(data){
					sports = data.message;
					sports.forEach(function(sport) {
						$("#sport-menu").append('<li><a href="#">'+sport['sport']+'</a></li>');
					});
				}
                	});


		});
		*/



}
