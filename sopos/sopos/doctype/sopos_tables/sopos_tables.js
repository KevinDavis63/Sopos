// Copyright (c) 2024, info@soradius.com and contributors
// For license information, please see license.txt

 frappe.ui.form.on("Sopos Tables", {
	refresh(frm) {


       // Add a button to generate and print QR code
        frm.add_custom_button(__('QR Code'), function() {
        	frappe.msgprint("Creating QR Code")
            // Call server-side method to generate QR code
            frappe.call({
				method: 'sopos.scan_qr_code_api.generate_qr_code',

                args: {
                    docname: frm.doc.name
                },
                callback: function(response) {
                    // Display the generated QR code
                    var qr_code = response.message;
                    if(qr_code) {
                        frappe.msgprint({
                            title: __('QR Code'),
                            indicator: 'green',
                            message: `<img src="${qr_code}" alt="QR Code">`
                        });
                    }
                }
            });
        });











	},
 });
