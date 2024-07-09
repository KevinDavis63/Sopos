import frappe
import sopos


@frappe.whitelist(allow_guest=True)
def login(**kwargs):
	users = frappe.get_all("User", filters={"name": kwargs.get("email")})
	client_doc = frappe.get_doc("SOPOS Settings")
	doc = frappe.get_doc("SOPOS Settings")
	if not doc:
		return sopos.api_error("Setup client id before proceeding")

	if not users:
		return sopos.api_error("Incorrect email and or password")
	if not frappe.utils.password.check_password(users[0].name, kwargs.get("password")):
		frappe.throw("Incorrect email and or password")
		#return sopos.api_error("Incorrect email and or password")
	# generate auth token here
	return sopos.create_bearer_token(users[0].name, doc.oauth_client_id)


@frappe.whitelist()
def active_user():
	user = frappe.get_all("User", filters={"name":frappe.session.user}, fields=["full_name","email","name"])
	if not user:
		return sopos.api_error("Account not found", 401)
	return user[0]


@frappe.whitelist(allow_guest=True)
def verify_account(**kwargs):
	users = frappe.get_all("User", filters={"name": kwargs.get("email")})
	if not users:
		return sopos.api_error("Incorrect email and or password")
	if not frappe.utils.password.check_password(users[0].name, kwargs.get("password")):
		return sopos.api_error("Incorrect email and or password")
	# generate auth token here
	return True



