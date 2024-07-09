# Copyright (c) 2024, info@soradius.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
import datetime


def execute(filters=None):
	if not filters: filters = {}

	data, columns = [], []

	columns = get_columns()
	cs_data = get_cs_data(filters)

	if not cs_data:
		return columns, cs_data

	data = []
	for d in cs_data:
		order = frappe.get_doc("Sopos Table Orders",d.parent)
		row = frappe._dict({
				'item_code': d.item_code,
				'status': d.status if d.status else 'Awaiting payment',
				'quantity': d.quantity,
				'price': d.price,
				'parent': d.parent,
				'table':order.table,
				'waiter':get_user(order.waiter),
				'date':d.modified
			})
		data.append(row)

	chart = get_chart_data(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart,report_summary
	#return columns, data

def get_user(email):
	users = frappe.get_all("User", filters={"name":email}, fields=["*"])
	return users[0].full_name if users and len(users) > 0 else ''


def get_columns():
	return [
		{
			'fieldname': 'item_code',
			'label': _('Item'),
			'fieldtype': 'Data',
			'width': '150'
		},
		{
			'fieldname': 'status',
			'label': _('Status'),
			'fieldtype': 'Data',
			'width': '150'
		},
		{
			'fieldname': 'parent',
			'label': _('Order'),
			'fieldtype': 'Data',
			'width': '150'
			
		},
		{
			'fieldname': 'table',
			'label': _('Table'),
			'fieldtype': 'Data',
			'width': '150'	
		},
		{
			'fieldname': 'waiter',
			'label': _('Waiter'),
			'fieldtype': 'Data',
			'width': '150'
		},
		{
			'fieldname': 'quantity',
			'label': _('Quantity'),
			'fieldtype': 'Data',
			'width': '100'
		},
		{
			'fieldname': 'price',
			'label': _('Price'),
			'fieldtype': 'Data',
			'width': '100'
		},
		{
			'fieldname': 'date',
			'label': _('Last Update'),
			'fieldtype': 'Datetime',
			'width': '150'
		},
	
	]

def get_cs_data(filters):
	conditions = get_conditions(filters)
	filters= {}
	print(conditions)
	if "item_code" in conditions:
		filters["item_code"] = conditions["item_code"]

	if "cancel_date" in conditions:
		given_date = datetime.datetime.strptime(conditions['cancel_date'], "%Y-%m-%d")
		start_of_day = datetime.datetime.combine(given_date.date(), datetime.time.min)
		end_of_day = datetime.datetime.combine(given_date.date(), datetime.time.max)
		filters["cancel_date"] = ["between", (start_of_day, end_of_day)]

	data = frappe.get_all(
		doctype='Sopos Table Order Items',
		fields=['*'],
		filters=filters,
		order_by='modified desc'
	)
	return data

def get_conditions(filters):
	conditions = {}
	for key, value in filters.items():
		if filters.get(key):
			conditions[key] = value

	return conditions


def get_chart_data(data):
	if not data:
		return None

	labels = ['Cancelled','Paid','Awaiting Payment']

	sale_data = {
		'Cancelled': 0,
		'Paid': 0,
		'Awaiting Payment':0
	}
	datasets = []

	for entry in data:
		print(entry.status)
		if entry.status == "Saved":
			sale_data['Awaiting Payment'] += 1
		if entry.status == "Awaiting payment":
			sale_data['Awaiting Payment'] += 1
			
		if entry.status == "Paid":
			sale_data['Paid'] += 1

		if entry.status == "Cancelled":
			sale_data['Cancelled'] += 1

	datasets.append({
		'name': 'Status',
		'values': [sale_data.get('Cancelled'),sale_data.get('Paid'),sale_data.get('Awaiting Payment')]
	})

	chart = {
		'data': {
			'labels': labels,
			'datasets': datasets
		},
		'type': 'bar',
		'height': 300,
	}

	return chart


def get_report_summary(data):
	if not data:
		return None
	pending, cancelled,paid = 0, 0, 0
	for entry in data:
		if entry.status == "Saved":
			pending += 1
		if not entry.status or entry.status == "Awaiting payment":
			pending += 1			
		if entry.status == "Paid":
			paid += 1

		if entry.status == "Cancelled":
			cancelled += 1

	return [
		{
			'value': pending,
			'indicator': 'Green',
			'label': 'Awaiting payment',
			'datatype': 'Int',
		},
		{
			'value': paid,
			'indicator': 'Blue',
			'label': 'Paid',
			'datatype': 'Int',
		},
		{
			'value': cancelled,
			'indicator': 'Red',
			'label': 'Cancelled',
			'datatype': 'Int',
		}
	]