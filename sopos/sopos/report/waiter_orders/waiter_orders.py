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
		total = 0
		if d.pos_invoice:
			invoices = frappe.get_all("POS Invoice", filters={"name":d.pos_invoice}, fields=["*"]);
			total = invoices[0].base_total if len(invoices) > 0 else 0
		row = frappe._dict({
				'item_code': d.item_code,
				'status': d.status,
				'table':d.table,
				'customer':d.customer,
				'waiter':get_user(d.waiter),
				'pos_invoice':d.pos_invoice,
				'total':total,
				'date':d.modified
			})
		data.append(row)
	return columns, data

def get_user(email):
	users = frappe.get_all("User", filters={"name":email}, fields=["*"])
	return users[0].full_name if users and len(users) > 0 else ''


def get_columns():
	return [
		{
			'fieldname': 'status',
			'label': _('Status'),
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
			'fieldname': 'customer',
			'label': _('Customer'),
			'fieldtype': 'Data',
			'width': '150'
		},
		{
			'fieldname': 'pos_invoice',
			'label': _('Invoice'),
			'fieldtype': 'Link',
			'options':"POS Invoice",
			'width': '150'
		},
		{
			'fieldname': 'total',
			'label': _('Amount'),
			'fieldtype':'Data',
			'width': '150'
		},
		{
			'fieldname': 'date',
			'label': _('Cancel Date'),
			'fieldtype': 'Datetime',
			'width': '150'
		},
	
	]

def get_cs_data(filters):
	conditions = get_conditions(filters)
	print(conditions)
	filters= {}
	if "waiter" in conditions:
		filters["waiter"] = conditions["waiter"]

	if "date" in conditions:
		given_date = datetime.datetime.strptime(conditions['date'], "%Y-%m-%d")
		start_of_day = datetime.datetime.combine(given_date.date(), datetime.time.min)
		end_of_day = datetime.datetime.combine(given_date.date(), datetime.time.max)
		filters["modified"] = ["between", (start_of_day, end_of_day)]

	data = frappe.get_all(
		doctype='Sopos Table Orders',
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

