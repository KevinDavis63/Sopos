// Copyright (c) 2024, info@soradius.com and contributors
// For license information, please see license.txt

 frappe.ui.form.on("Sopos Tables", {
 	refresh(frm) {

		  frm.add_custom_button(__('Generate QR code'), function(){
				//make http request to generate qrcode
			 frappe.call({
                method: 'sopos.api.v1.restaurant.plan.generate_qr_code',
                args: {
                    'docname': frm.doc.name
                },
                callback: function(response) {
                    if (response.message) {
                        // Create a new HTML element to display the QR code
                        var qr_code_html = '<div><img src="' + response.message + '" alt="QR Code" /></div>';
                        // Display the QR code in a dialog
                        var d = new frappe.ui.Dialog({
                            title: 'QR Code',
                            fields: [
                                { fieldtype: 'HTML', options: qr_code_html }
                            ],
                            primary_action_label: 'Print',
                            primary_action: function() {
                               var printWindow = window.open('', '_blank');
                                printWindow.document.write('<html><head><title>Print QR Code</title>');
                                printWindow.document.write('<style>body{display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}img{max-width:100%;height:auto;}</style>');
                                printWindow.document.write('</head><body>' + qr_code_html + '</body></html>');
                                printWindow.document.close();
                                printWindow.onload = function() {
                                    printWindow.print();
                                   /// printWindow.close();
                                };
                                d.hide();
                            }
                        });
                        d.show();
                    }
                }
            });

			}, __("Utilities"));
 	},
 });
