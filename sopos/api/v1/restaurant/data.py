import frappe
import sopos


@frappe.whitelist()
def init_data():
	tables = frappe.get_all("Sopos Tables", fields=["*"])
	floors = frappe.get_all("Sopos Floor", fields=["*"], order_by='creation asc')

	return {
		"tables": tables,
		"floors": floors,

	}


@frappe.whitelist()
def items(**kwargs):
	# items = frappe.get_all("Item", filters={"custom_isdrink": 1, "custom_isfood": 1})
	if kwargs.get("customer"):
		items = frappe.get_all("Item", fields=["*"])
		for item in items:
			item_price = get_price_list_rate(item.get("item_code"), "Standard Selling",
											 kwargs.get("customer"), transaction_date)
			item["price"] = item_price
		return {
			"items": items,

		}

	items = frappe.get_all("Item", fields=["*"])
	prices = frappe.get_all("Item Price", fields=["*"])
	taxes = frappe.get_all("Item Tax", fields=["*"])
	tax_template_detail = frappe.get_all("Item Tax Template Detail", fields=["*"])
	return {
		"items": items,
		"prices": prices,
		"taxes": taxes,
		"tax_template_detail": tax_template_detail,
	}


@frappe.whitelist()
def supervisors(**kwargs):
	settings = frappe.get_doc("SOPOS Settings")
	if not settings:
		return sopos.api_error("No supervisor role settings")

	user_emails = frappe.db.sql("""
	 	    SELECT *
	 	    FROM `tabHas Role`
	    	WHERE role = %s
			AND parenttype = "User"
	 	""", settings.change_approval_role, as_dict=True)
	users = []
	for user_email in user_emails:
		user_doc = frappe.get_doc("User", user_email.parent)
		if user_doc:
			user_data = {
				"full_name": user_doc.get("full_name"),
				"email": user_doc.get("email"),
			}
			users.append(user_data)

	return {
		"supervisors": users
	}


@frappe.whitelist()
def tables(**kwargs):
	if not kwargs.get("pos_opening_entry"):
		return []
	pos_opening = kwargs.get("pos_opening_entry")
	tables = frappe.get_all("Sopos Tables", fields=["*"])
	items = []
	for table in tables:
		orderItems = []
		orders = frappe.get_all("Sopos Table Orders",
								fields=["*"],
								filters={
									"pos_opening_entry": pos_opening,
									"table": table.name,
									"status": "Ordered"
								})
		#for order in orders:
		#	orderItems.append(frappe.get_doc("Sopos Table Orders", order.name))
		for order in orders:
			obj = frappe.get_doc("Sopos Table Orders", order.name)
			sum = 0
			mItemList = [];
			for mItem in obj.items:
				try:
					if float(mItem.quantity)!=0:
						mItemList.append(mItem);
						sum = sum +float(mItem.quantity)
				except ValueError:
					None
			obj.items = mItemList
			if sum >0:
				orderItems.append(obj)
		#for order in orders:
		#	items = frappe.get_all("Sopos Table Order Items",fields=["*"], filters=[["parent","=", order.name],["quantity","!=","0"]])
		#	order['items']= items
		#	orderItems.append(order)

		table.orders = orderItems

		qrOrderItems = []
		qrOrders = frappe.get_all("QR CODE ORDER", fields=["*"], filters={"table": table.name,"status":"Ordered"})
		for qrOrder in qrOrders:
			qrOrderItems.append(frappe.get_doc("QR CODE ORDER", qrOrder.name))
		table.qrOrderItems = qrOrderItems
		items.append(table)
	
	return {
		"tables": items
	}


@frappe.whitelist()
def pricing_rules(**kwargs):
	items = []
	rules = frappe.get_all("Pricing Rule", filters={
		"disable": 0
	})
	for rule in rules:
		items.append(frappe.get_doc("Pricing Rule", rule.name))

	return {
		"rules": items
	}
