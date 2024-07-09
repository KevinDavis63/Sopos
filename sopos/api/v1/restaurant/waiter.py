import frappe
import sopos


@frappe.whitelist()
def index():
	settings = frappe.get_doc("SOPOS Settings")
	if not settings:
		return sopos.api_error("No waiter role settings")

	user_emails = frappe.db.sql("""
	    SELECT parent
	    FROM `tabHas Role`
	    WHERE role = %s
	    AND parenttype = "User"
	""", settings.waiter_role, as_dict=True)

	# Extracting user emails from the result
	users = []
	for user_email in user_emails:
		user_doc = frappe.get_doc("User", user_email.parent)
		if user_doc:
			pincode = frappe.get_all("Sopos Pincode", filters={"user": user_doc.get("name")})
			pincode_exists = bool(pincode)
			user_data = {
				"full_name": user_doc.get("full_name"),
				"email": user_doc.get("email"),
				"pincode": pincode_exists
			}
			users.append(user_data)

	return {
		"waiters": users
	}


@frappe.whitelist()
def details(**kwargs):
	user_doc = frappe.get_doc("User", kwargs.get("email"))

	waiter = frappe.get_all("Sopos Pincode", filters={"user": kwargs.get("email")},
							fields=["user", "blocked"])
	if not waiter:
		return {
			"full_name": user_doc.full_name,
			"blocked": False,
			"pincode": False,
			"tries": 0
		}
	exists = bool(waiter)
	if not user_doc:
		return sopos.api_error("Account not found")

	return {
		"full_name": user_doc.full_name,
		"blocked": waiter[0].blocked,
		"tries": waiter[0].tries,
		"pincode": True,
	}
