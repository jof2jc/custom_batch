from __future__ import unicode_literals
import frappe
from frappe import _

from frappe.utils import nowdate, now_datetime
from frappe.model.document import Document


def update_batch_expiry_status(doc, method):
	#frappe.throw(doc.name)
	days_to_expiry = frappe.utils.date_diff(doc.expiry_date, nowdate())
	doc.days_to_expiry = days_to_expiry

	if int(days_to_expiry) <= int(doc.expiry_start_day) and int(days_to_expiry) > 30:
		doc.expiry_status = "Expired Soon"
	elif int(days_to_expiry) <= 30 and int(days_to_expiry) > 0:
		doc.expiry_status = "Expired Very Soon"
	elif int(days_to_expiry) <= 0:
		doc.expiry_status = "Expired"
	else:
		doc.expiry_status = "Open"

	doc.save()
	
	