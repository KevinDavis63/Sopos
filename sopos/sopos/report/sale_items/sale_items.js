// Copyright (c) 2024, info@soradius.com and contributors
// For license information, please see license.txt

frappe.query_reports["Sale Items"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "date",
			"label": __("Date"),
			"fieldtype": "Date",
			// "default": frappe.datetime.now_date(),
		}
	]
};

