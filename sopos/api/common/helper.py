import frappe
import africastalking


def send_sms_message(to, message):
    # send sms
    # frappe.sendmail(
    #     recipients=[to],
    #     sender='your_email@example.com',  # Replace with your email
    #     message=message,
    #     subject='SMS Notification',
    #     reference_doctype='Communication',
    #     reference_name='New SMS'
    # )
    at_setting = frappe.get_doc("Phone Authentication Settings")
    if at_setting:

        africastalking.initialize(username=at_setting.username, api_key=at_setting.api_key)
        sms = africastalking.SMS
        try:
            response = sms.send(message, to, at_setting.sender)
            print(response)
        except Exception as e:
            frappe.log_error(title="Sms Sending",
                             message="failed when sending sms to {} the sms is {}. The error message is {}".format(to,
                                                                                                                   message,
                                                                                                                   str(
                                                                                                                       e)))


def doctype_exist(doctype):
    try:
        frappe.get_meta(doctype)
        return True
    except frappe.DoesNotExistError:
        return False


def get_or_insert_document(doctype, filters, data):
    # Check if the document exists
    if frappe.db.exists(doctype, filters):
        # Document already exists, return it
        existing_doc = frappe.get_doc(doctype, filters)
        return existing_doc
    else:
        # Document doesn't exist, create a new one
        new_doc = frappe.new_doc(doctype)
        new_doc.update(data)
        new_doc.insert(ignore_permissions=True)
        return new_doc


def get_records(doc_type, filters, multiple=True):
    """
    Helper function to retrieve records from Frappe.

    Parameters:
    - doc_type (str): The DocType name.
    - conditions (dict): The conditions for the query.
    - multiple (bool): Flag indicating whether to retrieve one or multiple records.

    Returns:
    - Single document if multiple is False, otherwise a list of documents.
    """

    if multiple:
        return frappe.get_all(doc_type, filters=filters)
    else:
        return frappe.get_doc(doc_type, filters)


def create_bearer_token(mobile_no, client_id):
    otoken = frappe.new_doc("OAuth Bearer Token")
    otoken.access_token = frappe.generate_hash(length=30)
    otoken.refresh_token = frappe.generate_hash(length=30)
    otoken.user = frappe.db.get_value("User", {"mobile_no": mobile_no}, "name")
    otoken.scopes = "all"
    otoken.client = client_id
    otoken.redirect_uri = frappe.db.get_value("OAuth Client", client_id, "default_redirect_uri")
    otoken.expires_in = 30 * 86400
    otoken.save(ignore_permissions=True)
    frappe.db.commit()

    return otoken#{"token": otoken, "user_type": frappe.db.get_value("User", {"mobile_no": mobile_no}, "user_type")}
