// Copyright (c) 2024, lavaloon and contributors
// For license information, please see license.txt

function on_add_row_translations(frm, cdt, cdn)
{
    var parent_page_id = frm.doc.page;
    // Get the newly added row
    var row = locals[cdt][cdn];
    // Set the field value based on the parent DocType field
    row.page = parent_page_id;
    row.website_page_block = frm.doc.name;
    row.block_key = frm.doc.block_key;
    //var page_block_field = row.website_page_block;
    /*
    frm.set_query('website_page_block', 'translations', function() {
        return {
            filters: {
                "page": parent_page_id
            }
        };
    });
    */
    frm.refresh_field('translations');
}



frappe.ui.form.on('Website Page Block Translation', {
    translations_add: function(frm, cdt, cdn) {
        on_add_row_translations(frm,cdt,cdn);
     },
    translations_on_form_rendered: function(frm, cdt, cdn) {
        on_add_row_translations(frm,cdt,cdn);
    }
});

frappe.ui.form.on('Website Page Block', {
    validate: function(frm) {
        const translations_table = frm.doc.translations;
        const checked_values = {};

        for (let i = 0; i < translations_table.length; i++) {
            const row = translations_table[i];
            const language = row.language;

            // Check if key field value already exists (excluding current record)
            if (checked_values.hasOwnProperty(language) && checked_values[language] !== i) {
                frappe.throw(__('Duplicate value found for "language"!'));
                break;
            }
            checked_values[language] = i;
        }
    }
});