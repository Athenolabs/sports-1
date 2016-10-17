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

});
