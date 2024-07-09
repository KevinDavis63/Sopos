// Copyright (c) 2024, info@soradius.com and contributors
// For license information, please see license.txt

frappe.query_reports["Cancelled Items"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "cancel_date",
			"label": __("Cancel date"),
			"fieldtype": "Date",
			// "default": frappe.datetime.now_date(),
		}
	]
};
