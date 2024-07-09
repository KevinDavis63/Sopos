import frappe
import sopos


@frappe.whitelist(allow_guest=True)
def add(**kwargs):
	users = frappe.get_all("User", filters={"name": kwargs.get("email")})
	if not users:
		return sopos.api_error("User not found")
	codes = frappe.get_all("Sopos Pincode", filters={"user": kwargs.get("email")})
	for code in codes:
		frappe.delete_doc("Sopos Pincode", code.name)
	# create new pincode
	pin_doc = frappe.new_doc("Sopos Pincode")
	pin_doc.user = kwargs.get("email")
	pin_doc.pin = kwargs.get("code")
	pin_doc.tries = 0
	pin_doc.blocked = 0
	pin_doc.save()
	return True


@frappe.whitelist(allow_guest=True)
def verify(**kwargs):
	codes = frappe.get_all("Sopos Pincode", filters={
		"user": kwargs.get("email")
	})
	if not codes:
		return sopos.api_error("Pincode not setup")
	else:
		code = frappe.get_doc("Sopos Pincode", codes[0].name)
		if code.blocked == 1:
			return sopos.api_error("Pincode blocked  You can only reset the pincode")
		else:
			valid = bool(int(kwargs.get("code")) == int(code.pin))
			if valid:
				code.blocked = 0
				code.tries = 0
				code.save()
				return True
			else:
				if code.tries >= 2:
					code.tries = 3
					code.blocked = 1
					code.save()
				else:
					code.tries = code.tries + 1
					code.save()

				if code.tries >= 3:
					return sopos.api_error("Pincode blocked. You can only reset the pincode")
				else:
					return sopos.api_error(
						"Invalid pincode you have {} tries left".format(3 - code.tries))


@frappe.whitelist(allow_guest=True)
def remove(**kwargs):
	codes = frappe.get_all("Sopos Pincode", filters={
		"user": kwargs.get("email")
	})
	for code in codes:
		frappe.delete_doc("Sopos Pincode", code.name)
	return True
