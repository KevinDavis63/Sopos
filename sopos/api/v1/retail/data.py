import frappe


@frappe.whitelist()
def init_data():
	customers = frappe.get_all("Customer", fields=["*"])
	warehouse = frappe.get_all("Warehouse", fields=["*"])
	pos_profile = frappe.get_all("POS Profile", fields=["*"])
	item = frappe.get_all("Item", fields=["*"])
	payment_mode = frappe.get_all("Mode of Payment", fields=["*"])

	return {
		"customers": customers,
		"warehouses": warehouse,
		"pos_profiles": pos_profile,
		"items": item,
		"payment_modes": payment_mode,
	}
