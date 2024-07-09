import frappe
import qrcode
from io import BytesIO
import base64

@frappe.whitelist()
def generate_qr_code(docname):
	setting = frappe.db.get_single_value('SOPOS Settings', 'qr_code_domain')
	print(setting)
	if not setting:
		frappe.throw("Set domain url setting on the sopos settings inorder to generate qr code for the table")
	doc = frappe.get_doc("Sopos Tables", docname)
	qr_data = f"Table: {doc.name}"
	qr = qrcode.QRCode(
		version=1,
		error_correction=qrcode.constants.ERROR_CORRECT_L,
		box_size=10,
		border=4,
	)
	qr.add_data(qr_data)
	qr.make(fit=True)

	img = qr.make_image(fill='black', back_color='white')
	buffer = BytesIO()
	img.save(buffer, format="PNG")
	qr_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

	return f"data:image/png;base64,{qr_image_base64}"
@frappe.whitelist()
def save_floor(**kwargs):
	doc = frappe.new_doc("Sopos Floor")
	doc.floor_name = kwargs.get("floor_name")
	doc.company = kwargs.get("company")
	doc.save()
	return True


@frappe.whitelist()
def remove_floor(**kwargs):
	tables = frappe.get_list("Sopos Tables", filters={"floor": kwargs.get("name")})
	for table in tables:
		frappe.delete_doc("Sopos Tables", table.name)
	frappe.delete_doc("Sopos Floor", kwargs.get("name"))


@frappe.whitelist()
def rename_floor(**kwargs):
	frappe.db.set_value('Sopos Floor', kwargs.get("name"), {
		'floor_name': kwargs.get("floor_name"),
		'name': kwargs.get("floor_name")
	})
	frappe.db.commit()


# TABLES
@frappe.whitelist()
def add_table(**kwargs):
	doc = frappe.new_doc("Sopos Tables")
	doc.floor = kwargs.get("floor")
	doc.table_name = kwargs.get("name")
	doc.seats = kwargs.get("seats")
	doc.shape = kwargs.get("shape")
	doc.company = kwargs.get("company")
	doc.status = "Available"
	doc.save()
	return True


@frappe.whitelist()
def update_table(**kwargs):
	frappe.db.set_value('Sopos Tables', kwargs.get("name"), {
		'seats': kwargs.get("seats"),
		'shape': kwargs.get("shape"),
		'deleted': "No",
	})
	frappe.db.commit()
	return True


@frappe.whitelist()
def delete_table(**kwargs):
	frappe.delete_doc('Sopos Tables', kwargs.get("name"))
	# frappe.db.set_value('Sopos Tables', kwargs.get("name"), {
	# 	'deleted': "Yes",
	# })
	# frappe.db.commit()
	return True

@frappe.whitelist()
def update_table_resize(**kwargs):
	doc = frappe.get_doc("Sopos Tables",kwargs.get("name"))
	doc.height = kwargs.get("height")
	doc.width = kwargs.get("width")
	doc.deleted = "No"
	doc.save()
	return True

@frappe.whitelist()
def update_table_drag(**kwargs):
	doc = frappe.get_doc("Sopos Tables",kwargs.get("name"))
	doc.x = kwargs.get("x")
	doc.y = kwargs.get("y")
	doc.deleted = "No"
	doc.save()
	return True
