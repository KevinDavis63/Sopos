import json

import frappe
import frappe.utils
import requests
from erpnext.accounts.doctype.pricing_rule.pricing_rule import apply_pricing_rule, \
	get_pricing_rule_for_item
from frappe.utils.pdf import get_pdf
from frappe.utils.print_format import download_pdf
from frappe.utils import get_files_path
from sopos import api_error
import os


def create_production_order(**kwargs):
	tables = frappe.get_all("Sopos Tables", filters={"name": kwargs.get("table")}, fields=["*"])
	orders = frappe.get_all("Sopos Production Order", fields=["*"],
							filters={"order_no": kwargs.get("order_no")})
	receipts = []
	if not orders:
		for item in kwargs.get("production"):
			doc = frappe.new_doc("Sopos Production Order")
			doc.area = item.get("name")
			doc.table = tables[0].name
			doc.floor = tables[0].floor
			doc.customer = kwargs.get("customer")
			doc.order_no = kwargs.get("order_no")
			doc.company = kwargs.get("company")
			for child in item.get("items"):
				doc.append("items", {
					"item_code": child.get("item_code"),
					"quantity": child.get("quantity")
				})
			doc.save()

		# generate receipt
		return True
	else:
		# check those that have been removed and remove them
		for order in orders:
			doc = frappe.get_doc("Sopos Production Order", order.name)
			doc.table = tables[0].name
			doc.floor = tables[0].floor
			doc.customer = kwargs.get("customer")
			doc.order_no = kwargs.get("order_no")
			doc.company = kwargs.get("company")
			doc.set("items", [])
			doc.save()

			# update items in each area of doc
			for item in kwargs.get("production"):
				if item.get("name") == order.area:

					for child in item.get("items"):
						doc.append("items", {
							"item_code": child.get("item_code"),
							"quantity": child.get("quantity")
						})
			doc.save()
			frappe.db.commit()


@frappe.whitelist()
def book_table(**kwargs):
	doc = frappe.new_doc("Sopos Table Orders")
	doc.table = kwargs.get("table")
	doc.customer = kwargs.get("customer")
	doc.guests = kwargs.get("guest")
	doc.waiter = kwargs.get("waiter")
	doc.pos_opening_entry = kwargs.get("pos_opening_entry")
	doc.status = "Ordered"

	for child in kwargs.get("items"):
		doc.append("items", {
			"item_code": child.get("item_code"),
			"quantity": child.get("quantity"),
			"price": child.get("price"),
			"uom": child.get("uom"),
			"status": "Saved",
			"tax_rate": child.get("tax_rate"),
			"customer_note": child.get("customer_note"),
			"internal_note": child.get("internal_note"),
		})
	doc.append("history", {
		"status":"Ordered",
		"created_by":kwargs.get("waiter"),
		"date":frappe.utils.now()
	})
	doc.save()


	frappe.db.commit()

	# also create a production order request here
	kwargs["order_no"] = doc.name
	create_production_order(**kwargs)
	return doc


@frappe.whitelist()
def update_order(**kwargs):
	isQrOrder = kwargs.get("isQrOrder")
	if isQrOrder==True:			#Add By Kevin
		doc = book_table(**kwargs)
		qrDoc = frappe.get_doc("QR CODE ORDER",kwargs.get("order_no"))
		qrDoc.status="Accepted"
		qrDoc.save()
		frappe.db.commit()
	else:
		doc = frappe.get_doc("Sopos Table Orders", kwargs.get("order_no"))
		doc.table = kwargs.get("table")
		doc.customer = kwargs.get("customer")
		doc.guests = kwargs.get("guest")
		doc.waiter = kwargs.get("waiter")
		doc.pos_opening_entry = kwargs.get("pos_opening_entry")
		doc.status = "Ordered"
		doc.set("items", [])
		doc.save()
		for child in kwargs.get("items"):
			doc.append("items", {
				"item_code": child.get("item_code"),
				"quantity": child.get("quantity"),
				"price": child.get("price"),
				"tax_rate": child.get("tax_rate"),
				"uom": child.get("uom"),
				"customer_note": child.get("customer_note"),
				"internal_note": child.get("internal_note"),
				"status":"Saved"
			})
		doc.save()
		frappe.db.commit()

		kwargs["order_no"] = doc.name
		create_production_order(**kwargs)

	return doc

@frappe.whitelist()
def unpaid_items(**kwargs):
	existingItems = frappe.get_all("Sopos Table Order Items", filters={
		"parent": kwargs.get("order_no"),
		"status": "Saved"
	})

	return existingItems

@frappe.whitelist()
def submit_order(**kwargs):
	setting = frappe.get_doc("SOPOS Settings")
	if not setting.tax_account:
		return api_error("Tax account not setup")
	doc = frappe.new_doc("POS Invoice")
	doc.customer = kwargs.get("customer")
	doc.custom_waiter = kwargs.get("waiter")
	doc.company = kwargs.get("company")
	doc.posting_date = kwargs.get("posting_date")
	doc.pos_profile = kwargs.get("pos_profile")
	doc.is_pos = kwargs.get("is_pos")
	doc.custom_pos_opening_entry = kwargs.get("opening_entry")
	doc.update_stock = kwargs.get("update_stock")
	if (kwargs.get("pay_later")):
		doc.change_amount = "0"
	else:
		doc.change_amount = kwargs.get(	"change_amount")

	if (kwargs.get("pay_later")):
		doc.base_change_amount = 0
	else:
		doc.base_change_amount = kwargs.get("change_amount")

	doc.append("taxes", {
		"charge_type": "Actual",
		"description": "VAT tax",
		"account_head": setting.tax_account,
		"tax_amount": kwargs.get("tax_amount")
	})
	for child in kwargs.get("items"):
		quantity = float(child.get("quantity"))
		price = float(child.get("price"))
		amount = quantity * price
		doc.append("items", {
			"item_code": child.get("item_code"),
			"qty": quantity,
			"rate": price,  # child.get("price"),
			"base_rate": price,  # child.get("price"),
			"amount": amount
		})
		existingItems = frappe.get_all("Sopos Table Order Items", filters={
			"parent": kwargs.get("table_order_no"),
			"item_code":child.get("item_code"),
			"status":"Saved"
		})
		for item in existingItems:
			elem = frappe.get_doc("Sopos Table Order Items",item.name)
			elem.status = "Paid"
			elem.save()


	for child in kwargs.get("payments"):
		doc.append("payments", {
			"mode_of_payment": child.get("mode_of_payment"),
			"amount": float(child.get("amount")),
		})
	if (kwargs.get("pay_later")):
		doc.status = "Overdue"
		doc.outstanding_amount = kwargs.get("total_outstanding")
	doc.save(ignore_permissions=True)
	doc.submit()

	# update table order with payment
	order = frappe.get_doc("Sopos Table Orders", kwargs.get("table_order_no"))
	#update order status

	if (kwargs.get("pay_later")):
		order.status = "PayLater"
	else:
		#check if there are items not paid yet
		unpaid = frappe.get_all("Sopos Table Order Items", filters={
			"parent":order.name,
			"status":"Saved"
		})
		if unpaid:
			order.status = "Ordered"
		else:
			order.status = "Paid"
			# delete the production order
			production = frappe.get_all("Sopos Production Order",
										filters={"order_no": kwargs.get("table_order_no")})
			for item in production:
				frappe.delete_doc("Sopos Production Order", item.name)

	order.save(ignore_permissions=True)
	return doc


def generate_pdf(doctype, docname):
	pdf_content = frappe.utils.print_format.download_pdf(doctype, docname, format="PDF")


@frappe.whitelist()
def generate_html(**kwargs):
	doc = frappe.get_doc(kwargs.get("doc"), kwargs.get("name"))
	html = frappe.get_print(kwargs.get("doc"), doc.name, doc=doc, as_pdf=False,
							print_format="POS Invoice")
	return {
		"html": html
	}


@frappe.whitelist()
def generate_print(**kwargs):
	doc = frappe.get_doc("POS Invoice", kwargs.get("invoice_no"))
	pdf = frappe.get_print("POS Invoice", doc.name, doc=doc, as_pdf=True,
						   print_format="POS Invoice")

	filename = "{}.pdf".format(kwargs.get("invoice_no"))
	pdf_path = os.path.join(get_files_path("", is_private=0), filename)
	with open(pdf_path, "wb") as f:
		f.write(pdf)

	return {
		"url": "/files/" + filename
	}


@frappe.whitelist()
def invoice_details(**kwargs):
	invoice = frappe.get_doc("POS Invoice", kwargs.get("invoice_no"))
	return {
		"invoice": invoice
	}


@frappe.whitelist()
def production_areas(**kwargs):
	areas = frappe.get_all("Sopos Production Order",
						   filters={"order_no": kwargs.get("table_order_no")}, fields=["*"])
	return {
		"areas": areas
	}


@frappe.whitelist()
def generate_production_receipt(**kwargs):
	doc = frappe.get_doc("Sopos Production Order", kwargs.get("name"))
	pdf = frappe.get_print("Sopos Production Order", doc.name, doc=doc, as_pdf=True,
						   print_format="Production Center")

	filename = "{}.pdf".format(kwargs.get("name"))
	pdf_path = os.path.join(get_files_path("", is_private=0), filename)
	with open(pdf_path, "wb") as f:
		f.write(pdf)

	return {
		"url": "/files/" + filename
	}


@frappe.whitelist()
def active_orders(**kwargs):
	orders = frappe.get_all("Sopos Table Orders",
							fields=["*"],
							filters={
								"status": "Ordered",
								"pos_opening_entry": kwargs.get("pos_opening_entry")
							})
	items = []
	for order in orders:
		items.append(
			frappe.get_doc("Sopos Table Orders", order.name)
		)

	return {
		"items": items
	}


@frappe.whitelist()
def update_quantity(**kwargs):
	orders = frappe.get_all("Sopos Table Order Items",
							fields=["*"],
							filters={
								"item_code": kwargs.get("item_code"),
								"parent": kwargs.get("order_no")
							})
	for order in orders:
		if kwargs.get("quantity") == 0:

			item = frappe.get_doc("Sopos Table Order Items", order.name)
			item.status = "Cancelled"
			item.cancelled_by = kwargs.get("waiter")
			item.cancel_date = frappe.utils.now()
			item.approved_cancel_by = kwargs.get("supervisor")
			item.save()

			#frappe.delete_doc("Sopos Table Order Items", order.name)
		else:
			doc = frappe.get_doc("Sopos Table Order Items", order.name)
			doc.quantity = kwargs.get("quantity")
			doc.save()


@frappe.whitelist()
def get_price(**kwargs):
	details = get_pricing_rule_for_item(frappe.as_json({
		"doctype": "Item",
		"item_code": "Pawpaw",
	}), doc="Item")
	return details


@frappe.whitelist()
def remove_all(**kwargs):
	orders = frappe.get_all("Sopos Table Order Items",
							fields=["*"],
							filters={
								"parent": kwargs.get("order_no")
							})
	for order in orders:
		item = frappe.get_doc("Sopos Table Order Items", order.name)
		item.status = "Cancelled"
		item.cancelled_by = kwargs.get("waiter")
		item.cancel_date = frappe.utils.now()
		item.approved_cancel_by = kwargs.get("supervisor")
		item.save()
		#frappe.delete_doc("Sopos Table Order Items", order.name)


@frappe.whitelist()
def cancel_order(**kwargs):
	docs = frappe.get_all("Sopos Production Order", filters={
		"order_no": kwargs.get("order_no")
	})
	for doc in docs:
		frappe.delete_doc("Sopos Production Order", doc.name)

	orders = frappe.get_all("Sopos Table Orders", fields=["*"], filters={
			"name":kwargs.get("order_no")
		})
	for order in orders:
		orderItem = frappe.get_doc("Sopos Table Orders", order.name)
		orderItem.status = "Cancelled"
		orderItem.save()

		items = frappe.get_all("Sopos Table Order Items",
								fields=["*"],
								filters={
									"parent": order.name
								})
		for itemP in items:
			item = frappe.get_doc("Sopos Table Order Items", itemP.name)
			item.status = "Cancelled"
			item.cancelled_by = kwargs.get("waiter")
			item.cancel_date = frappe.utils.now()
			item.approved_cancel_by = kwargs.get("supervisor")
			item.save()
