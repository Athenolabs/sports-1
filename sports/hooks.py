# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "sports"
app_title = "Sports"
app_publisher = "Africlouds Ltd"
app_description = "Sports Management"
app_icon = "octicon octicon-file-directory"
app_color = "green"
app_email = "arwema@africlouds.com"
app_license = "MIT"

fixtures = [
"Web Page"
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sports/css/sports.css"
# app_include_js = "/assets/sports/js/sports.js"

# include js, css files in header of web template
# web_include_css = "/assets/sports/css/sports.css"
# web_include_js = "/assets/sports/js/sports.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "sports.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
#website_generators = ["Sport","Tournament"]

# Installation
# ------------

# before_install = "sports.install.before_install"
# after_install = "sports.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sports.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
 	"Game Event": {
 		"after_insert": "sports.api.update_standings_after_event",
		"after_insert": "sports.api.send_notifications"
	}
 }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sports.tasks.all"
# 	],
# 	"daily": [
# 		"sports.tasks.daily"
# 	],
# 	"hourly": [
# 		"sports.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sports.tasks.weekly"
# 	]
# 	"monthly": [
# 		"sports.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "sports.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sports.event.get_events"
# }

