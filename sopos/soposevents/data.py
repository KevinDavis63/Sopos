import frappe


def on_update(doc, method=None):
    print("\n\n\n LISTENING TO ITEM EVENT \n\n\n\n\n")
    frappe.publish_realtime("update_data", "{'message':'test','custom_app'}")
