// Copyright (c) 2016, Africlouds Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Season', {
	update_standings: function(frm) {
		frappe.call({
			method: "sports.api.update_standings",
			args: {
				season: frm.doc.name
			}
		});
	},
	enrol_teams: function(frm) {
		frappe.call({
			method: "sports.api.enrol_teams",
			args: {
				season: frm.doc.name
			}
		});
	},
	refresh: function(frm) {

	}
});
