import frappe


@frappe.whitelist()
def user_shift(**kwargs):
	shifts = frappe.get_all("Sopos Waiter Shift",
							fields=["*"],
							filters={
								"user": kwargs.get("email"),
								"pos_opening_entry": kwargs.get("pos_opening_entry"),
								"status": "Open"
							})
	return {
		"shifts": shifts
	}


@frappe.whitelist()
def start_shift(**kwargs):
	shifts = frappe.get_all("Sopos Waiter Shift", filters={
		"user": kwargs.get("email"),
		"pos_opening_entry": kwargs.get("pos_opening_entry"),
		"closing_date": None
	})
	for shift in shifts:
		frappe.delete_doc("Sopos Waiter Shift", shift.name)

	doc = frappe.new_doc("Sopos Waiter Shift")
	doc.user = kwargs.get("email")
	doc.pos_opening_entry = kwargs.get("pos_opening_entry")
	doc.opening_date = frappe.utils.now()
	doc.status = "Open"
	doc.save()

@frappe.whitelist()
def close_shift(**kwargs):
	shifts = frappe.get_all("Sopos Waiter Shift", filters={
		"user": kwargs.get("email"),
		"pos_opening_entry": kwargs.get("pos_opening_entry"),
		"closing_date": None
	})
	for shift in shifts:
		doc = frappe.get_doc("Sopos Waiter Shift", shift.name)
		doc.status = "Closed"
		doc.save()
