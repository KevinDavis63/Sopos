// Copyright (c) 2024, info@soradius.com and contributors
// For license information, please see license.txt

frappe.query_reports["Waiter Orders"] = {
	"filters": [
		{
			"fieldname": "waiter",
			"label": __("Waiter"),
			"fieldtype": "Link",
			"options": "User"
		},
		{
			"fieldname": "date",
			"label": __("Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.now_date(),
		}
	]
};
