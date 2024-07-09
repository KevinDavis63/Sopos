// Copyright (c) 2024, info@soradius.com and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Payments"] = {
	"filters": [
		{
			"fieldname": "date_from",
			"label": __("Date from"),
			"fieldtype": "Date",
			//"default": frappe.datetime.now_date(),
		},
		{
			"fieldname": "date_to",
			"label": __("Date to"),
			"fieldtype": "Date",
			//"default": frappe.datetime.now_date(),
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company"
			//"default": frappe.datetime.now_date(),
		},

	]
};
