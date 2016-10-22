# -*- coding: utf-8 -*-
# Copyright (c) 2015, Africlouds Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Game(Document):
	def validate(self):
		self.description = "%s VS %s D-%i %s" % (self.host_team, self.guest_team, self.day if self.day else 0, self.season)

	@frappe.whitelist() 
	def update_score(self):
		if self.status in ["Playing","Played"]:
			goals_host = frappe.db.count("Game Event", filters={"game": self.name, "team":self.host_team, 'type':'Goal'})
			goals_guest = frappe.db.count("Game Event", filters={"game": self.name, "team":self.guest_team, 'type':'Goal'})
			self.host_team_score = goals_host if goals_host else 0
			self.guest_team_score = goals_guest if goals_guest else 0
			self.score = "%i - %i" % (self.host_team_score, self.guest_team_score)

			self.save()
			frappe.db.commit()
	def kick_off(self):
		self.status = "Playing"
		self.save()
		frappe.db.commit()

	def end(self):
		self.status = "Played"
		self.save()
		frappe.db.commit()
		

