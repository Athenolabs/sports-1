# -*- coding: utf-8 -*-
# Copyright (c) 2015, Africlouds Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.website.website_generator import WebsiteGenerator


class Sport(WebsiteGenerator):
	website = frappe._dict(
                template = "templates/generators/sport.html"
        )

        def validate(self):
                self.route = "sport/"+self.name

