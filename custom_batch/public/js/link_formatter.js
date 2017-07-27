frappe.form.link_formatters['Batch'] = function(value, doc) {
    if(doc.expiry_date) {
        return value + ': ' + doc.expiry_date;
    } else {
        return value;
    }
}