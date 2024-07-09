# Copyright (c) 2024, info@soradius.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
import datetime
from collections import defaultdict


def execute(filters=None):
	if not filters: filters = {}

	columns, data = [], []
	columns = get_columns()

	data = get_cs_data(filters)

	return columns, data, None, None, None

def get_columns():
	return [
		{
			'fieldname': 'mode',
			'label': _('Mode of payment'),
			'fieldtype': 'Data',
			'width': '200'
		},
		{
			'fieldname': 'amount',
			'label': _('Amount'),
			'fieldtype': 'Data',
			'width': '200'
		}
	]

def get_cs_data(filters):
	conditions = get_conditions(filters)
	filters= {}

	if all(key in conditions for key in ('date_from', 'date_to')):
		filters["modified"] = ["between", (conditions["date_from"], conditions["date_to"])]
	else:
		return []

	if 'company' in conditions:
		filters["company"] =  conditions["company"]
	else:
		return []
	invoices = frappe.get_all(
		doctype='POS Invoice',
		fields=['*'],
		filters=filters,
		order_by='modified desc'
	)
	# Dictionary to store payment modes and their amounts
	payment_modes = defaultdict(float)

	# Iterate through POS invoices to retrieve payments

	values = []
	for invoice in invoices:
		# Retrieve payments for each POS invoice from Sales Invoice Payment child table
		payments = frappe.get_all(
			doctype='Sales Invoice Payment',
			fields=['mode_of_payment', 'amount'],
			filters={'parent': invoice['name']}
		)
		# Sum up amounts for each payment mode

		total_amount = 0
		for payment in payments:
			total_amount += float(payment.amount) 
		
		if(total_amount == 0.0):
			values.append({"mode":"Pay Later", "amount":invoice["total"]})
		else:
			for payment in payments:
				values.append({"mode":payment["mode_of_payment"], "amount":payment["amount"]})


	mode_totals = defaultdict(float)
	# Iterate through payments
	for payment in values:
		mode = payment["mode"]
		amount = float(payment["amount"])
		mode_totals[mode] += amount

		# Create an array to store the final output
	output = []

	# Add each mode and its total to the output array
	for mode, amount in mode_totals.items():
		output.append({"mode": mode, "amount": amount})
		
	return output

def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value

	return conditions
