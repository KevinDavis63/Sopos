import frappe
import qrcode
from io import BytesIO
import base64
from frappe.utils import nowdate, nowtime


@frappe.whitelist()
def generate_qr_code(docname):
	# Get the domain setting from SOPOS Settings
	domain_url = frappe.db.get_single_value('SOPOS Settings', 'qr_code_domain')
	if not domain_url:
		frappe.throw("Set domain URL in the SOPOS Settings to generate QR code for the table")

	# Get the document details
	doc = frappe.get_doc("Sopos Tables", docname)
	
	# Construct the URL with doc.name as a query parameter
	qr_url = f"http://{domain_url}/order-items-list/?table_name={doc.name}"  # Adjust the URL path as needed
	# Prepare the data to be encoded in the QR code
	qr_data = {
		"table_name": doc.name,
		"url": qr_url
	}

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






@frappe.whitelist(allow_guest=True)
def get_items():
	items = frappe.db.sql("""
		SELECT
			item.name,
			item.description,
			item_price.price_list_rate AS price,
			item.image
		FROM
			`tabItem` AS item
		JOIN
			`tabItem Price` AS item_price
		ON
			item.name = item_price.item_code
		WHERE
			item.disabled = 0
		ORDER BY
			item.creation DESC
		LIMIT 40
	""", as_dict=True)

	return items







import frappe
from frappe.utils import now_datetime

@frappe.whitelist(allow_guest=True)
def create_table_order():
	frappe.log_error(" create_table_order ", "create_table_order ")
	try:
		data = frappe.form_dict
		if data:
			pos_opening_entry = get_or_create_latest_open_pos_entry()
			frappe.log_error("Data Found", "Data Found")
			doc = frappe.new_doc("Sopos Table Orders")
			doc.table = data.get("table") or "T21"
			doc.customer = "Walk In"
			doc.guests = 0
			doc.waiter = pos_opening_entry.get("user")
			doc.pos_opening_entry = pos_opening_entry.get("name")
			doc.status = "Ordered"
			items = data.get("items")
			if isinstance(items, str):
				items = frappe.parse_json(items)
				
			if not isinstance(items, list):
				frappe.throw("Invalid items format. Must be a list of dictionaries.")
			
			for child in items:
				if not isinstance(child, dict):
					frappe.throw("Invalid item format. Each item must be a dictionary.")
				
				doc.append("items", {
					"item_code": child.get("item_code"),
					"quantity": child.get("quantity"),
					"price": child.get("price"),
					"uom":  "Nos" or child.get("uom"),
					"status": "Saved",
					# "tax_rate": child.get("tax_rate"),
					# "customer_note": child.get("customer_note"),
					# "internal_note": child.get("internal_note"),
				})
			
			doc.append("history", {
				"status": "Ordered",
				"created_by": data.get("waiter", ""),
				"date": frappe.utils.now()
			})

			doc.insert(
				ignore_permissions=True, # ignore write permissions during insert
				ignore_links=True, # ignore Link validation in the document
				ignore_if_duplicate=True, # don't insert if DuplicateEntryError is thrown
				ignore_mandatory=True # insert even if mandatory fields are not set
			)

			doc.save(ignore_permissions=True)
			frappe.db.commit()
			create_Sopos_Production_Order(doc)
			frappe.log_error("Created create_table_order ", "create_table_order ")
			return doc
		
		return data

	except Exception as e:
		error_message = frappe.get_traceback() + "\n{}".format(str(e))
		frappe.log_error(error_message, "General Error create_table_order")
		truncated_message = error_message[:140]  # Limit to 140 characters for logging
		return {"error": truncated_message}










def get_or_create_latest_open_pos_entry():
	# Fetch the latest open POS Opening Entry name
	pos_opening_entry = {}
	latest_entry = frappe.get_all('POS Opening Entry', 
								  filters={"docstatus": 1}, 
								  fields=["name","user", "pos_profile"], 
								  order_by="posting_date desc, period_start_date desc", 
								  limit_page_length=1)
	
	if latest_entry:
		# Retrieve the document using frappe.get_doc
		pos_opening_entry = frappe.get_doc('POS Opening Entry', latest_entry[0].name)
		return pos_opening_entry
	else:
		# Create a new POS Opening Entry
		pos_opening_entry = frappe.get_doc({
			"doctype": "POS Opening Entry",
			"posting_date": nowdate(),
			"period_start_date": now(),
			"user": "shah@lectuspro.com",
			"pos_profile": "Blue Groud Floor",
			"docstatus": 0,  # Set to draft; change to 1 if you want to submit immediately
			# Add other required fields here
		})
		pos_opening_entry.insert(
			ignore_permissions=True, # ignore write permissions during insert
			ignore_links=True, # ignore Link validation in the document
			ignore_if_duplicate=True, # don't insert if DuplicateEntryError is thrown
			ignore_mandatory=True # insert even if mandatory fields are not set
		)
		pos_opening_entry.save(ignore_permissions=True)
		frappe.db.commit()  # Commit to save the new document
	return pos_opening_entry











def create_Sopos_Production_Order(doc):
	production_order = frappe.new_doc("Sopos Production Order")
	production_order.area = "Kitchen";
	production_order.customer =  "Walk In";
	production_order.company = "Blue";
	production_order.floor = "Ground Floor";
	production_order.order_no = doc.get("name");
	production_order.table = doc.get("table");
	for child in doc.get("items"):
		production_order.append("items", {
			"item_code": child.get("item_code"),
			"quantity": child.get("quantity")
		})
	production_order.insert(
		ignore_permissions=True, # ignore write permissions during insert
		ignore_links=True, # ignore Link validation in the document
		ignore_if_duplicate=True, # don't insert if DuplicateEntryError is thrown
		ignore_mandatory=True # insert even if mandatory fields are not set
	)
	production_order.save(ignore_permissions=True)
	frappe.db.commit()  # Commit to save the new document

