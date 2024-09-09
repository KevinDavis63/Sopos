import frappe
import sopos
from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import (
	make_closing_entry_from_opening,
)
from frappe.utils.background_jobs import enqueue

@frappe.whitelist()
def open(**kwargs):
	p_entry = kwargs.get("open_entry")
	if p_entry != '':
		entrys = frappe.get_all("POS Opening Entry",
							fields=["*"],
							filters=[
								{"name": p_entry }
							])
		if entrys:
			return entrys[0]
	doc = frappe.new_doc("POS Opening Entry")
	doc.customer = kwargs.get("customer")
	doc.period_start_date = kwargs.get("period_start_date")
	doc.pos_profile = kwargs.get("pos_profile")
	doc.posting_date = kwargs.get("posting_date")
	doc.status = "Open"
	doc.user = frappe.session.user
	for item in kwargs.get("balance"):
		doc.append("balance_details", {
			"mode_of_payment": item.get("mode_of_payment"),
			"opening_amount": item.get("opening_amount"),
		})
	doc.insert(ignore_permissions=True)
	doc.submit()
	return doc


@frappe.whitelist()
def get_opening_entry(**kwargs):
	entrys = frappe.get_all("POS Opening Entry",
							fields=["*"],
							filters=[
								{"name": kwargs.get("name"), }
							])

	if not entrys:
		return sopos.api_error(message="Unable to find the opening entry", code=500)

	return entrys[0]


@frappe.whitelist()
def opening_entry_details(**kwargs):
	opening_entry = frappe.get_doc("POS Opening Entry", kwargs.get("pos_opening_entry"))
	payment_modes = frappe.get_all("Mode of Payment", fields=["*"])

	sales = frappe.get_all("POS Invoice", filters={
		"custom_pos_opening_entry": kwargs.get("pos_opening_entry")
	}, fields=["*"])
	sales_data = [frappe.get_doc("POS Invoice", d.name).as_dict() for d in sales]

	return {
		"opening_entry": opening_entry,
		"sales": sales_data,
		"modes":payment_modes,
	}

# @frappe.whitelist()
# def close_pos(**kwargs):
# 	opening_entry = frappe.get_doc("POS Opening Entry", kwargs.get("pos_opening_entry"))
# 	if not opening_entry:
# 		return sopos.api_error(message="OPening entry not found", code=500)
# 	doc = make_closing_entry_from_opening(opening_entry)

# 	doc.set("payment_reconciliation",None)

# 	for item in kwargs.get("amount"):
# 		doc.append("payment_reconciliation", {
# 			"mode_of_payment": item.get("mode_of_payment"),
# 			"opening_amount": item.get("opening_amount"),
# 			"expected_amount": item.get("expected_amount"),
# 			"closing_amount": item.get("closing_amount"),
# 			"difference":item.get("difference")
# 		})

# 	doc.save(ignore_permissions=True)
# 	doc.submit()
# 	# frappe.delete_doc("Sopos Production Order")
# 	return doc

@frappe.whitelist()
def close_pos(**kwargs):
	opening_entry = frappe.get_doc("POS Opening Entry", kwargs.get("pos_opening_entry"))


	if not opening_entry:
		return sopos.api_error(message="OPening entry not found", code=500)
	doc = frappe.new_doc("POS Closing Entry")
	doc.period_start_date = opening_entry.period_start_date
	doc.posting_date = opening_entry.posting_date
	doc.period_end_date = frappe.utils.nowdate()
	doc.posting_time = frappe.utils.nowtime()
	doc.pos_opening_entry = opening_entry.name
	doc.company = opening_entry.company
	doc.user = frappe.session.user
	doc.grand_total = kwargs.get("grand_total")
	doc.net_total = kwargs.get("net_total")
	doc.base_net_total = kwargs.get("base_net_total")
	doc.custom_pay_later_amount = kwargs.get("pay_later")
	doc.total_quantity = kwargs.get("total_quantity")
	doc.status = "Submitted"
	for item in kwargs.get("amount"):
		doc.append("payment_reconciliation", {
			"mode_of_payment": item.get("mode_of_payment"),
			"opening_amount": item.get("opening_amount"),
			"expected_amount": item.get("expected_amount"),
			"closing_amount": item.get("closing_amount"),
			"difference":item.get("difference")
		})
	for item in kwargs.get("pos_invoices"):
		doc.append("pos_transactions", {
			"pos_invoice": item.get("pos_invoice"),
			"customer": item.get("customer"),
			"posting_date": item.get("posting_date"),
			"grand_total": item.get("grand_total"),
		})
	doc.save(ignore_permissions=True)
	doc.submit()
	email_closed_pos(doc)
	frappe.delete_doc("Sopos Production Order")
	return doc

def email_closed_pos(closed_doc):
	receiver = 'mmauricio@catertradebn.com'

	if receiver:
		email_args = {
				"sender": "bluerestaurant2024@gmail.com",
				"recipients": [receiver, "hragab@catertradebn.com" ],
				"message": "Pos Closing Entry",
				"subject": "Pos Closing Entry --- " + closed_doc.posting_date.strftime("%Y-%m-%d %H:%M:%S"),
				"attachments": [
					frappe.attach_print(closed_doc.doctype, closed_doc.name, file_name=closed_doc.name, password=None)
				],
				"reference_doctype": closed_doc.doctype,
				"reference_name": closed_doc.name,
				"now":True
			}
		# if not frappe.flags.in_test:
		# 	enqueue(method=frappe.sendmail, queue="short", timeout=300, is_async=True, **email_args)
		# else:
		frappe.sendmail(**email_args)
	else:
		return False


