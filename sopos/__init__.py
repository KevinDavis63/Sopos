__version__ = "0.0.1"

import frappe
from werkzeug import Response


def api_error(message, code=500):
	frappe.response['http_status_code'] = 500  # HTTP 400 Bad Request
	response = Response('{"message": "' + message + '"}', content_type='application/json',
						status=code)
	return response


def create_bearer_token(email, client_id):
	otoken = frappe.new_doc("OAuth Bearer Token")
	otoken.access_token = frappe.generate_hash(length=30)
	otoken.refresh_token = frappe.generate_hash(length=30)
	otoken.user = frappe.db.get_value("User", {"email": email}, "name")
	otoken.scopes = "all"
	otoken.client = client_id
	otoken.redirect_uri = frappe.db.get_value("OAuth Client", client_id, "default_redirect_uri")
	otoken.expires_in = 30 * 86400
	otoken.save(ignore_permissions=True)
	frappe.db.commit()
	return {
		"token": otoken.access_token
	}
