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
			'fieldname': 'item_code',
			'label': _('Item name'),
			'fieldtype': 'Data',
			'width': '150'
		},
		{
			'fieldname': 'quantity',
			'label': _('Qty'),
			'fieldtype': 'Data',
			'width': '150'
		},
		{
			'fieldname': 'rate',
			'label': _('Rate'),
			'fieldtype': 'Data',
			'width': '150'
		},
		{
			'fieldname': 'total',
			'label': _('Total'),
			'fieldtype': 'Data',
			'width': '150'
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

	data = frappe.get_all(
		doctype='POS Invoice',
		fields=['*'],
		filters=filters,
		order_by='modified desc'
	)

	item_totals = defaultdict(lambda: {'quantity': 0, 'rate': 0})

	# Iterate through each POS Invoice
	for invoice in data:
		items = frappe.get_all(
			doctype='POS Invoice Item',
			fields=['item_code', 'qty', 'rate'],
			filters={'parent': invoice['name']}
		)
		for item in items:
			item_code = item.get('item_code')
			quantity = item.get('qty', 0)
			rate = item.get('rate', 0)
			# Update the quantity and rate for the item code, considering the highest rate
			item_totals[item_code]['quantity'] += quantity
			item_totals[item_code]['rate'] = max(item_totals[item_code]['rate'], rate)

	final = []
	for item_code, values in item_totals.items():
		quantity = values['quantity']
		rate = values['rate']
		total = quantity * rate
		final.append({'item_code': item_code, 'quantity': quantity, 'rate': rate, 'total': total})

	return final

def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value

	return conditions
