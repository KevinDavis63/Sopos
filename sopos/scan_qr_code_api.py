import frappe
import qrcode
from io import BytesIO
import base64
from frappe.utils import nowdate, nowtime, now_datetime
import json

@frappe.whitelist()
def generate_qr_code(docname):
	try:
		# Get the domain setting from SOPOS Settings
		domain_url = frappe.db.get_single_value('SOPOS Settings', 'qr_code_domain')
		if not domain_url:
			frappe.throw("Set domain URL in the SOPOS Settings to generate QR code for the table")

		# Get the document details
		doc = frappe.get_doc("Sopos Tables", docname)
		# Construct the URL with doc.name as a query parameter
		qr_url = f"http://{domain_url}/order-items-list/?table_name={doc.name}"
		# Generate QR code
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data(qr_url)
		qr.make(fit=True)
		img = qr.make_image(fill='black', back_color='white')
		buffer = BytesIO()
		img.save(buffer, format="PNG")
		qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

		return f"data:image/png;base64,{qr_image_base64}"
	except Exception as e:
		error_message = frappe.get_traceback() + "\nError: " + str(e)
		frappe.log_error(error_message, "Generate QR Code: Error")
		frappe.throw("An error occurred while generating the QR code.")

@frappe.whitelist(allow_guest=True)
def get_items(item_group=0):
	try:
		items = frappe.db.sql("""
			SELECT
				item.name,
				item.description,
				item_price.price_list_rate AS price,
				item.image,
				item.item_group
			FROM
				`tabItem` AS item
			JOIN
				`tabItem Price` AS item_price
			ON
				item.name = item_price.item_code
			WHERE
				item.disabled = 0
				AND item.item_group = %s
			ORDER BY
				item.name DESC
		""", (item_group,), as_dict=True)
		return items
	except Exception as e:
		error_message = frappe.get_traceback() + "\nError: " + str(e)
		frappe.log_error(error_message, "Get Items: Error")
		frappe.throw("An error occurred while fetching the items.")

@frappe.whitelist(allow_guest=True)
def get_item_groups():
	try:
		items = frappe.db.sql(f"""SELECT name,docstatus,parent_item_group,is_group,idx FROM `tabItem Group` where idx!=0 ORDER BY creation""", as_dict=True)
		return items
	except Exception as e:
		error_message = frappe.get_traceback() + "\nError: " + str(e)
		frappe.log_error(error_message, "Get Item Groups: Error")
		frappe.throw("An error occurred while fetching the items.")

@frappe.whitelist(allow_guest=True)
def get_item_group():
	try:
		item_groups = frappe.db.sql("""
			SELECT
				ig.item_group AS item_group
			FROM
				`tabRestaurant Food Item Group` AS ig
			WHERE 1=1 
			ORDER BY
				ig.item_group ASC
		""", as_dict=True)
		return return_response_message_dict(data=item_groups, error="", response_code=True, message="Item Category List.")
	except Exception as e:
		error_message = frappe.get_traceback() + "\nError: " + str(e)
		frappe.log_error(error_message, "Get Item Group: Error")
		return return_response_message_dict(data={}, error=error_message, response_code=False, message="Error while fetching item category.")

@frappe.whitelist(allow_guest=True)
def get_items_by_item_group(item_group=0):
	if item_group:
		try:
			items = frappe.db.sql("""
				SELECT
					item.name,
					item.item_code,
					item.item_group,
					item.description,
					item_price.price_list_rate AS price,
					item.image
				FROM
					`tabItem` AS item
				INNER JOIN
					`tabItem Price` AS item_price
				ON
					item.name = item_price.item_code
				INNER JOIN
					`tabItem Group` AS item_group
				ON
					item.item_group = item_group.name
				WHERE
					item.disabled = 0
					AND item.item_group = %s
				ORDER BY
					item.creation DESC
			""", (item_group,), as_dict=True)
			return return_response_message_dict(data=items, error="", response_code=True, message="Item list by category.")
		except Exception as e:
			error_message = frappe.get_traceback() + "\nError: " + str(e)
			frappe.log_error(error_message, "Get Items by Item Group: Error")
			return return_response_message_dict(data={}, error=error_message, response_code=False, message="Error while fetching items by category.")
	else:
		frappe.log_error("Parameter Missing.", "Get Items by Item Group: Error")
		error_message = "Item group parameter missing"
		return return_response_message_dict(data={}, error=error_message, response_code=False, message="Item group parameter missing.")

@frappe.whitelist(allow_guest=True)
def create_qrcode_order(doc={}):
	doc = frappe.local.form_dict
	if doc:
		try:
			if isinstance(doc, str):
				doc = json.loads(doc)
			new_doc = frappe.new_doc("QR CODE ORDER")
			new_doc.company = "Blue"
			# new_doc.floor = "Ground Floor"
			new_doc.table = doc.get("table")  or "T25"
			items = json.loads(doc.get("items"))
			for child in items:
				if isinstance(child, str):
					child = json.loads(child)
				if child and child != "undefined" and child !=None:
					new_doc.append("item_ordered", {
						"item_code": child.get("item_code"),
						"quantity": child.get("quantity") or 0,
						"price": child.get("price") or 0,
						"tax": child.get("tax_rate") or 0,
						"uom": "Nos",
						"total_amount":   0  ,
					})
			new_doc.insert(
				ignore_permissions=True,
				ignore_links=True,
				ignore_if_duplicate=True,
				ignore_mandatory=True
			)
			new_doc.save(ignore_permissions=True)
			frappe.db.commit()  # Commit to save the new document
			return return_response_message_dict(data=new_doc, error="", response_code=True, message="Record Created")
		except Exception as e:
			error_message = frappe.get_traceback() + "\nError: " + str(e)
			frappe.log_error(error_message, "Create QR Code Order: Error")
			return return_response_message_dict(data={}, error=error_message, response_code=False, message="Error while creating QR code order.")
	else:
		frappe.log_error("Parameter Missing.", "Create QR Code Order: Error")
		return return_response_message_dict(data={}, error="Parameter missing", response_code=False, message="Parameter missing.")

# frappe.whitelist(allow_guest=True)
# def create_qrcode_order(doc={}):
# 	if doc:
# 		try:
# 			if isinstance(doc, str):
# 				doc = json.loads(doc)
# 			new_doc = frappe.new_doc("QR CODE ORDER")
# 			new_doc.company = "Blue"
# 			# new_doc.floor = "Ground Floor"
# 			new_doc.table = doc.get("table")  or "T25"
# 			for child in doc.get("items"):
# 				if child and child != "undefined":
# 					new_doc.append("items", {
# 						"item_code": child.get("itemName"),
# 						"quantity": child.get("quantity") or 0,
# 						"price": child.get("rate") or 0,
# 						"uom": "Nos",
# 						"total_amount":   0  ,
# 					})
# 			new_doc.insert(
# 				ignore_permissions=True,
# 				ignore_links=True,
# 				ignore_if_duplicate=True,
# 				ignore_mandatory=True
# 			)
# 			new_doc.save(ignore_permissions=True)
# 			frappe.db.commit()  # Commit to save the new document
# 			return return_response_message_dict(data=new_doc, error="", response_code=True, message="Record Created")
# 		except Exception as e:
# 			error_message = frappe.get_traceback() + "\nError: " + str(e)
# 			frappe.log_error(error_message, "Create QR Code Order: Error")
# 			return return_response_message_dict(data={}, error=error_message, response_code=False, message="Error while creating QR code order.")
# 	else:
# 		frappe.log_error("Parameter Missing.", "Create QR Code Order: Error")
# 		return return_response_message_dict(data={}, error="Parameter missing", response_code=False, message="Parameter missing.")

def return_response_message_dict(data={}, error="", response_code=False, message=""):
	return {
		"data": data,
		"error": error,
		"response_code": response_code,
		"message": message
	}
