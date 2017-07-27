from __future__ import unicode_literals
import frappe
from frappe import _

from frappe.utils import nowdate, now_datetime

def set_item_name(self, method):
	self.item_name = self.item_code

@frappe.whitelist()
def get_batch_no_fifo(item_code=None, warehouse=None):
	data={}
	return frappe.db.sql('''SELECT ste.batch_no, sum(ste.actual_qty) as qty FROM `tabStock Ledger Entry` ste Inner Join `tabBatch` b 
			ON ste.item_code=b.item AND ste.batch_no=b.name WHERE b.days_to_expiry > 0 and b.expiry_status Not IN('Expired') 
			AND ste.item_code=%s and ste.warehouse=%s GROUP BY ste.batch_no HAVING sum(ste.actual_qty) > 0 
			ORDER BY ste.posting_date ASC,ste.posting_time ASC limit 1''', (item_code, warehouse), as_dict=0)
				

def set_batch_expired_date_from_purchase(self, method):
	#batch_doc = frappe.get_doc("Batch", batch_id)
	#pi_doc = frappe.get_doc("Purchase Invoice", pi_name)

	for d in self.items:
		has_batch_no = frappe.db.get_value('Item', d.item_code, 'has_batch_no')
		if has_batch_no and d.batch_no:
			batch_doc = frappe.get_doc("Batch", d.batch_no)

			#batch_doc.expiry_date = d.expired_date

			#batch_doc.expiry_start_day = d.expiry_start_day
			batch_doc.reference_doctype = self.doctype
			batch_doc.reference_name = self.name

			days_to_expiry = frappe.utils.date_diff(batch_doc.expiry_date, nowdate())
			batch_doc.days_to_expiry = days_to_expiry

			if int(days_to_expiry) <= int(d.expiry_start_day) and int(days_to_expiry) > 30:
				batch_doc.expiry_status	= "Expired Soon"
			elif int(days_to_expiry) <= 30 and int(days_to_expiry) > 0:
				batch_doc.expiry_status	= "Expired Very Soon"
			elif int(days_to_expiry) <= 0:
				batch_doc.expiry_status	= "Expired"
			else:
				batch_doc.expiry_status	= "Open"

			batch_doc.save()
			#frappe.throw(_("Expiry date for Batch {0} is {1}").format(d.batch_no, batch_doc.expiry_date))

def update_batch_expiry_status(batch_doc, method):
	#frappe.throw(_("hai"))
	#batch_doc = frappe.get_doc("Batch", self.name)
	days_to_expiry = frappe.utils.date_diff(batch_doc.expiry_date, nowdate())
	batch_doc.days_to_expiry = days_to_expiry

	if int(days_to_expiry) <= int(batch_doc.expiry_start_day) and int(days_to_expiry) > 30:
		batch_doc.expiry_status = "Expired Soon"
	elif int(days_to_expiry) <= 30 and int(days_to_expiry) > 0:
		batch_doc.expiry_status = "Expired Very Soon"
	elif int(days_to_expiry) <= 0:
		batch_doc.expiry_status = "Expired"
	else:
		batch_doc.expiry_status = "Open"

	batch_doc.save()
	#frappe.throw(_("Expiry Status for Batch {0} is {1}").format(self.name, self.expiry_status))

def update_batch_expired_date_daily():
	batch_items = frappe.db.sql ("""SELECT name, item, expiry_date, expiry_start_day FROM `tabBatch`
		where expiry_date <> '' and days_to_expiry >= 0 and expiry_status <> 'Expired'""", as_dict=1)

	for d in batch_items:
		if d.expiry_date:
			batch_doc = frappe.get_doc("Batch", d.name)
			days_to_expiry = frappe.utils.date_diff(d.expiry_date, nowdate())
			batch_doc.days_to_expiry = days_to_expiry

			if int(days_to_expiry) <= int(d.expiry_start_day) and int(days_to_expiry) > 30:
				batch_doc.expiry_status	= "Expired Soon"
			elif int(days_to_expiry) <= 30 and int(days_to_expiry) > 0:
				batch_doc.expiry_status	= "Expired Very Soon"
			elif int(days_to_expiry) <= 0:
				batch_doc.expiry_status	= "Expired"
			else:
				batch_doc.expiry_status	= "Open"

			batch_doc.save()

def get_notification_config():
	return {
		"for_doctype": {
			#"Batch": "custom_batch.custom_batch.custom_batch.get_expiry_batches"
			"Batch": {
				"expiry_status": ("in", ("Expired Soon", "Expired Very Soon"))
			}
		}
	}

def get_expiry_batches(as_list=False):
	"""Returns a count of incomplete todos"""
	#data = frappe.db.sql("""Select count(*) from `tabBatch` where days_to_expiry >= 0""", as_list=True)
	data = frappe.get_list("Batch",
		fields=["name", "days_to_expiry"] if as_list else "count(*)",
		filters=[["Batch", "days_to_expiry", ">=", "0"]],
		as_list=True)

	if as_list:
		return data
	else:
		return data[0][0]
