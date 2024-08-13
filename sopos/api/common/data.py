import frappe


@frappe.whitelist()
def init_data():
	customers = frappe.get_all("Customer", fields=["*"])
	warehouse = frappe.get_all("Warehouse", fields=["*"])
	pos_profile = frappe.get_all("POS Profile", fields=["*"])
	items = frappe.get_all("Item", fields=["*"],filters=[{"disabled":"0"}])
	bin = frappe.get_all("Bin", fields=["*"])
	open_entries=frappe.get_all("POS Opening Entry",fields=["*"],filters=[{"status":"Open"},{ "docstatus": "1" }])
	payment_mode = frappe.get_all("Mode of Payment", fields=["*"])
	companies = frappe.get_all("Company", fields=["*"])
	settings = frappe.get_doc("SOPOS Settings")
	uoms = frappe.get_all("UOM")
	groups = frappe.get_all("Item Group", fields=["*"])

	return {
		"customers": customers,
		"warehouses": warehouse,
		"pos_profiles": pos_profile,
		"open_entries": open_entries,
		"items": items,
		"bin": bin,
		"payment_modes": payment_mode,
		"companies": companies,
		"settings": settings,
		"uoms": uoms,
		"groups": groups,
	}
