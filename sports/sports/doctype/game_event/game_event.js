// Copyright (c) 2016, Africlouds Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Game Event', {
        update_standings: function(frm) {
                frappe.call({
                        method: "sports.api.update_standings",
                        args: {
                                game_event: frm.doc.name
                        }
                });
        },

	refresh: function(frm) {

	}
});
