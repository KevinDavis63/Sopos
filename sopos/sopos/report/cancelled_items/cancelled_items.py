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
				'status': d.status,
				'parent': d.parent,
				'table':order.table,
				'waiter':get_user(order.waiter),
				'cancelled_by':get_user(d.cancelled_by),
				'approved_by':get_user(d.approved_cancel_by),
				'date':d.cancel_date
			})
		data.append(row)

	chart = get_chart_data(data)
	report_summary = get_report_summary(data)
	# return columns, data, None, chart,report_summary
	return columns, data

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
			'fieldname': 'cancelled_by',
			'label': _('Cancelled by'),
			'fieldtype': 'Data',
			'width': '150'
		},
		{
			'fieldname': 'approved_by',
			'label': _('Approved by'),
			'fieldtype': 'Data',
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
	filters= {
		"status":"Cancelled"
	}
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

	labels = ['Age <= 45','Age > 45']

	age_data = {
		'Age > 45': 0,
		'Age <= 45': 0,
	}
	datasets = []

	for entry in data:
		if entry.item_code == "PawPaw":
			age_data['Age <= 45'] += 1
			
		else:
			age_data['Age > 45'] += 1

	datasets.append({
		'name': 'Age Status',
		'values': [age_data.get('Age <= 45'),age_data.get('Age > 45')]
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
	age_below_45, age_above_45 = 0, 0

	for entry in data:
		if entry.item_code == 'Pawpaw':
			age_below_45 += 1
			
		else:
			age_above_45 += 1
	return [
		{
			'value': age_below_45,
			'indicator': 'Green',
			'label': 'Age Below 45',
			'datatype': 'Int',
		},
		{
			'value': age_above_45,
			'indicator': 'Red',
			'label': 'Age Above 45',
			'datatype': 'Int',
		}
	]