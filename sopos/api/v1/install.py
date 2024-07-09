import frappe


@frappe.whitelist(allow_guest=True)
def confirm():
	return True
