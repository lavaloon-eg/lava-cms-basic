
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

function get_content_list_records(page_id, frm, html_field){
    frappe.call({
        method: "lava_cms_basic.utils.localization.get_page_content_list",
        args: {
          page_id: page_id,
        },
        callback: function(data) {
            let html_content = load_content_list_records(data.message);
            html_field.set_value(html_content);
        }
      });
}

function load_content_list_records(records){
    var html = `<br/>
                <label style="display: inline-block; font-weight: bold;">Page's blocks and translations summary</label>
                <br/>
                <div>
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
        let page_id = frm.doc.name;
        let html_field = $('[data-fieldname="content_list"]')[0].fieldobj;
        //alert(html_field.get_content());
        get_content_list_records(page_id, frm, html_field);
     }
});