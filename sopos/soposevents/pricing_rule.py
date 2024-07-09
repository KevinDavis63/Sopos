import frappe


def on_update(doc, method=None):
    frappe.publish_realtime("update_rules", "{'message':'test','custom_app'}")
