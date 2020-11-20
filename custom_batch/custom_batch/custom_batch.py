from __future__ import unicode_literals
import frappe
from frappe import _

from frappe.utils import nowdate, now_datetime, flt, formatdate, get_datetime
import json
import datetime

def set_item_name(self, method):
	self.item_name = self.item_code

@frappe.whitelist()
def get_last_purchase_rate(item_code=None, warehouse=None):
	return frappe.db.sql('''select item_code, incoming_rate from 
				`tabStock Ledger Entry`	where item_code=%s and voucher_type='Purchase Invoice' and ifnull(incoming_rate,0) <> 0 
				order by posting_date desc, posting_time desc limit 1''', item_code, as_dict=0)

@frappe.whitelist()
def get_last_purchase_rate2(item_code=None, warehouse=None):
	return frappe.db.sql('''select result_wrapper.item_code, result_wrapper.base_rate from 
				(select
					result.item_code,
					result.base_rate
					from (
						(select
							po_item.item_code,
							po_item.item_name,
							po.transaction_date as posting_date,
							po_item.base_price_list_rate,
							po_item.discount_percentage,
							(po_item.base_rate / po_item.conversion_factor) as base_rate
						from `tabPurchase Order` po, `tabPurchase Order Item` po_item
						where po.name = po_item.parent and po.docstatus = 1)
						union
						(select
							pr_item.item_code,
							pr_item.item_name,
							pr.posting_date,
							pr_item.base_price_list_rate,
							pr_item.discount_percentage,
							(pr_item.base_rate / pr_item.conversion_factor) as base_rate
						from `tabPurchase Receipt` pr, `tabPurchase Receipt Item` pr_item
						where pr.name = pr_item.parent and pr.docstatus = 1)
						union
						(select
							pi_item.item_code,
							pi_item.item_name,
							pi.posting_date,
							pi_item.base_price_list_rate,
							pi_item.discount_percentage,
							(pi_item.base_rate / pi_item.conversion_factor) as base_rate
						from `tabPurchase Invoice` pi, `tabPurchase Invoice Item` pi_item
						where pi.name = pi_item.parent and pi.docstatus = 1)
					) result
					order by result.item_code asc, result.posting_date desc) result_wrapper
					where item_code=%s group by item_code limit 1''', item_code, as_dict=0)

@frappe.whitelist()
def get_batch_no_fifo(item_code=None, warehouse=None):
	data={}
	return frappe.db.sql('''SELECT ste.batch_no, sum(ste.actual_qty) as qty FROM `tabStock Ledger Entry` ste Inner Join `tabBatch` b 
			ON ste.item_code=b.item AND ste.batch_no=b.name WHERE b.days_to_expiry > 0 and b.expiry_status Not IN ('Not Set','Expired') 
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
		where expiry_date <> '' and datediff(expiry_date,curdate()) <= 120 
		and expiry_status NOT IN ('Not Set','Expired')""", as_dict=1)

	for d in batch_items:
		if d.expiry_date:
			from erpnext.stock.doctype.batch.batch import get_batch_qty
			batch_qty = get_batch_qty(d.name, "DM Arcadia - MS", None)

			batch_doc = frappe.get_doc("Batch", d.name)
			days_to_expiry = frappe.utils.date_diff(d.expiry_date, nowdate())
			batch_doc.days_to_expiry = days_to_expiry
			
			
			if batch_qty and flt(batch_qty) <= 0:
				batch_doc.expiry_date = nowdate()
				batch_doc.expiry_status	= "Expired"
				batch_doc.days_to_expiry = 0
			elif int(days_to_expiry) <= int(d.expiry_start_day) and int(days_to_expiry) > 30:
				batch_doc.expiry_status	= "Expired Soon"
			elif int(days_to_expiry) <= 30 and int(days_to_expiry) > 0:
				batch_doc.expiry_status	= "Expired Very Soon"
			elif int(days_to_expiry) <= 0:
				batch_doc.expiry_status	= "Expired"
			else:
				batch_doc.expiry_status	= "Open"

			batch_doc.save()

def update_batch_expired_patch():
	batch_items = frappe.db.sql ("""SELECT name, item, expiry_date, expiry_start_day FROM `tabBatch`
		where expiry_status IN ('Expired')""", as_dict=1)

	for d in batch_items:
		if formatdate(d.expiry_date) == "06-09-2017":
			from erpnext.stock.doctype.batch.batch import get_batch_qty
			batch_qty = get_batch_qty(d.name, "DM Arcadia - MS", None)
			#frappe.throw(_("batch qty is {0}").format(batch_qty))
			batch_doc = frappe.get_doc("Batch", d.name)
			#days_to_expiry = frappe.utils.date_diff(d.expiry_date, nowdate())
			#batch_doc.days_to_expiry = days_to_expiry

			if flt(batch_qty) > 0:
				_data = frappe.db.sql ("""SELECT data from `tabVersion` where docname=%s and ref_doctype='Batch' order by modified desc limit 1""", d.name, as_dict=0)
				#frappe.throw(_("{0}").format(_data))
				_data = json.loads(_data[0][0])
				_changes = _data.get("changed")
				#frappe.throw(_("{0}").format(_changes))

				if _changes:
					print(d.name)
					batch_doc.days_to_expiry = _changes[2][1]
					batch_doc.expiry_status	= _changes[0][1]
					batch_doc.expiry_date = get_datetime(formatdate(_changes[1][1]))
				

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
