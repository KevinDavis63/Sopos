import frappe


@frappe.whitelist()
def index(**kwargs):
	codes = frappe.get_all("Sopos Pincode", fields=["user", "blocked"])
	return codes

@frappe.whitelist()
def save(**kwargs):
	user = frappe.get_doc("User",kwargs.get("email"))
	existing = frappe.get_all("Sopos Pincode", fields =["*"], filters={
		"user":kwargs.get("email")
	})
	if existing:
		codeItem = frappe.get_doc("Sopos Pincode", existing[0].name)
		codeItem.pin = kwargs.get("code")
		codeItem.tries = 0
		codeItem.blocked = 0
		codeItem.save()
	else:
		codeItem = frappe.new_doc("Sopos Pincode")
		codeItem.pin = kwargs.get("code")
		codeItem.user = kwargs.get("email")
		codeItem.tries = 0
		codeItem.blocked = 0
		codeItem.save()

	return True
