frappe.listview_settings['Batch'] = {
	add_fields: ["expiry_status"],
	get_indicator: function (doc) {
		return [__(doc.expiry_status), {
			"Expired": "grey",
			"Expired Soon": "orange",
			"Expired Very Soon": "red",
			"Open": "green",
			"Not Set": "darkgrey",
		}[doc.expiry_status], "expiry_status,=," + doc.expiry_status];
	}

};
/*
frappe.listview_settings['Batch'] = {
	get_indicator: function(doc) {
		if(doc.expiry_date && frappe.datetime.get_diff(doc.expiry_date) >= 0) {
			return [__("Expired"), "red", "days_to_expiry,<=,expiry_start_day"]
		} else if(doc.expiry_date) {
			return [__("Not Expired"), "green", "expiry_date,<,Today"]
		} else {
			return ["Not Set", "darkgrey", ""];
		}
	}
};
*/