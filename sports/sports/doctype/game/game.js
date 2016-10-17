// Copyright (c) 2016, Africlouds Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Game', {
	refresh: function(frm) {

	},
	update_game_score: function(frm) {
                frappe.call({
                        method: "sports.doctype.game.update_score",
                        args: {
                                Game: frm.doc.name
                        }
                });
        },
	load_host_lineups: function(frm) {
                frappe.call({
                        method: "sports.api.load_lineups",
                        args: {
                                game: frm.doc.name,
				team: "host"
                        }
                });
        },
	load_guest_lineups: function(frm) {
                frappe.call({
                        method: "sports.api.load_lineups",
                        args: {
                                game: frm.doc.name,
				team: "guest"
                        }
                });
        },

	reset_host_lineups: function(frm) {
                frappe.call({
                        method: "sports.api.reset_lineups",
                        args: {
                                game: frm.doc.name,
				team: "host"
                        }
                });
        },
	reset_guest_lineups: function(frm) {
                frappe.call({
                        method: "sports.api.reset_lineups",
                        args: {
                                game: frm.doc.name,
				team: "guest"
                        }
                });
        }

});
