# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "custom_batch"
app_title = "Custom Batch"
app_publisher = "Jonathan"
app_description = "Count Batch Expiry Days daily and create notification"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "jof2jc@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/custom_batch/css/custom_batch.css"
# app_include_js = "/assets/custom_batch/js/custom_batch.js"
app_include_js = [
	"assets/js/custom_batch1.min.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/custom_batch/css/custom_batch.css"
# web_include_js = "/assets/custom_batch/js/custom_batch.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
doctype_list_js = {
  "Batch": "public/js/batch_list.js"
}

fixtures = ["Custom Field", "Custom Script", "Property Setter"]


# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "custom_batch.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "custom_batch.install.before_install"
# after_install = "custom_batch.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "custom_batch.notifications.get_notification_config"

notification_config = "custom_batch.custom_batch.custom_batch.get_notification_config"

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
    "Stock Entry": {
        "on_submit": "custom_batch.custom_batch.custom_batch.set_batch_expired_date_from_purchase"
    },
    "Purchase Invoice": {
        "on_submit": "custom_batch.custom_batch.custom_batch.set_batch_expired_date_from_purchase"
    },
    "Item": {
        "validate": "custom_batch.custom_batch.custom_batch.set_item_name",
	"before_insert": "custom_batch.custom_batch.custom_batch.set_item_name"
    }
}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"custom_batch.tasks.all"
# 	],
# 	"daily": [
# 		"custom_batch.tasks.daily"
# 	],
# 	"hourly": [
# 		"custom_batch.tasks.hourly"
# 	],
# 	"weekly": [
# 		"custom_batch.tasks.weekly"
# 	]
# 	"monthly": [
# 		"custom_batch.tasks.monthly"
# 	]
# }

scheduler_events = {
	"daily": [
		"custom_batch.custom_batch.custom_batch.update_batch_expired_date_daily"
	]
}

# Testing
# -------

# before_tests = "custom_batch.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "custom_batch.event.get_events"
# }

