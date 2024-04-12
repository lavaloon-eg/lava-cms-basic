
// Function for content trimming (current formation shows first 20 words ... last 5 words)
function shortenContent(content) {
    if (!content || content === ""){
        return '';
    }

    let words = content.split(" ");
    let first_part_length = 20;
    let last_part_length = 5;
    if (words.length <= 20){
        first_part_length = words.length;
        last_part_length = 0;
    }else if(words.length  <= 25){
        first_part_length = 20;
        last_part_length = 25 - words.length;
    }
    let shortenedContent =
      words.slice(0, first_part_length).join(" ") + " ... " + words.slice(words.length-last_part_length,words.length,1).join(" ");
    return shortenedContent;
}

function add_field(parent_filed, label, id, type, doctype, options=null){
    var field_obj = null;
        if (type.toLowerCase() == 'data'){
            field_html = `<label for="${id}" class="control-label" style="padding-right: 0px;">${label}</label>
                            <input type="text" class="input-with-feedback form-control" style="width: 40%;" name="${id}" id="${id}" maxlength="140" data-fieldtype="Data" data-fieldname="${id}" data-doctype="${doctype}">
                            </input><br/>`;
            field_obj = $(field_html).appendTo(parent_filed);
        }
        else if(type.toLowerCase() == 'select'){
            field_html = `<label class="control-label" style="padding-right: 0px;">${label}</label>`;
            $(field_html).appendTo(parent_filed);
            field_html = `<select class="form-control" style="width: 40%;" name="${id}" id="${id}" data-fieldtype="Select" data-fieldname="${id}" data-doctype="${doctype}">`;
            field_obj = $(field_html).appendTo(parent_filed);
            var select_options = options;
            $.each(select_options, function(index, option) {
                var opt = $('<option>').attr('value', option).text(option);
                $(field_obj).append(opt);
            });
            $(parent_filed).append(`</select><br/>`);
        }
    return field_obj;
}

function get_content_list_records(frm){
    var page_id = frm.doc.name;
    var html_field = $('[data-fieldname="content_list"]')[0].fieldobj;
    var filters = {
            "language": $("#filter_language").val(),
            "block_title": $("#filter_block_title").val(),
            "block_key": $("#filter_block_key").val()
    };
    frappe.call({
        method: "lava_cms_basic.utils.localization.get_page_content_list",
        args: {
          page_id: page_id,
          filters: filters
        },
        callback: function(data) {
            let html_content = load_content_list_records(data.message);
            html_field.set_value(html_content);
        }
      });
}

function load_content_list_records(records){
    var html = `<div>
                <table style="border-collapse: collapse; width: 95%; border: 1px solid black;">
                    <thead>
                        <tr>
                            <th style="width: 25%;">Block Title</th>
                            <th style="width: 25%;">Block key</th>
                            <th style="width: 10%;">Language</th>
                            <th style="width: 40%;">Part of the content</th>
                        </tr>
                    </thead>
                    <tbody>`;
    if (records.length > 0){
        records.forEach(function(record) {
            let language = record.language;
            if (!language || language === ""){
                language = '';
            }
            html += `<tr style="border: 1px solid black;">
                        <td><a href="../website-page-block/${record.block_id}">${record.block_title}</a></td>
                        <td>${record.block_key}</td>
                        <td>${language}</td>
                        <td>${shortenContent(record.content)}</td>
                    </tr>`;
        });
    }
    html += `</tbody></table></div><br/>`

    return html;
}

frappe.ui.form.on('Website Page', {
    onload_post_render: function(frm) {
        get_content_list_records(frm);
    },
    onload: function(frm) {

        var filters = frm.fields_dict['filters_container'].wrapper;
        var filter_block_title = add_field(parent_filed=filters, label="Block Title", id="filter_block_title", type="Data", doctype="Website Page");
        var filter_block_key = add_field(parent_filed=filters, label="Block Key", id="filter_block_key", type="Data", doctype="Website Page");
        var filter_language = add_field(parent_filed=filters, label="Language", id="filter_language", type="Select", doctype="Website Page", options=['All', 'en', 'ar']);

        $(filter_block_title).on('change', function() {
            //var filter_key = $(this).val();
            //alert("Block title changed to: " + filter_key);
            get_content_list_records(frm);
        });

        $(filter_block_key).on('change', function() {
            //var filter_key = $(this).val();
            //alert("Block Key changed to: " + filter_key);
            get_content_list_records(frm);
        });

        $(filter_language).on('change', function() {
            //var selected_language = $(this).val();
            //alert("Language changed to: " + selected_language);
            get_content_list_records(frm);
        });
    }
});