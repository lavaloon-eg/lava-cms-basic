import frappe
import json

def get_default_language_key():
    """
    returns the default language key from website settings
    """
    lang_key = frappe.db.get_single_value('Website Page Settings', 'default_lang')
    if lang_key:
        return str(lang_key)
    else:
        return 'en'

@frappe.whitelist()
def format_language_key(language_key, default_language_key: str | None = None):
    """
    set the session language of the user. The method identifies the language based on
    the first 2 letters lower case. If not en (English), this means ar (Arabic)
    """
    default_language_key = default_language_key or get_default_language_key()
    if len(language_key) < 2:
        frappe.throw(msg="the language key's length must be >=2 characters",
                     exc=ValueError)
    selected_language = default_language_key
    if language_key[:2].lower() == "en":
        selected_language = "en"
    return selected_language


@frappe.whitelist()
def get_page_content_list(page_id: str, filters=None):
    if not page_id:
        frappe.msgprint('Make sure of selecting an existing page')
        return

    filters = json.loads(filters)

    sql = f"""
            SELECT b.name AS block_id,
                b.title AS block_title,
                b.block_key,
                t.language,
                t.content
            FROM `tabWebsite Page Block` AS b
            LEFT JOIN
                `tabWebsite Page Block Translation` AS t
                ON b.name = t.website_page_block
            WHERE
                b.page = %(page_id)s
            """

    if filters:
        if filters["language"] and filters["language"] != "All":
            sql += f"""
                    AND t.language = %(language)s
                    """
        if filters["block_key"]:
            sql += f"""
                    AND b.block_key LIKE %(block_key)s
                    """
        if filters["block_title"]:
            sql += f"""
                    AND b.title LIKE %(block_title)s
                    """

    sql += f"""
            ORDER BY b.title, b.block_key, t.language
            """
    records = frappe.db.sql(sql, values={
        "page_id": page_id,
        "language": filters["language"],
        "block_key": f"%{filters['block_key']}%",
        "block_title": f"%{filters['block_title']}%"
    }, as_dict=1)
    return records


def add_update_translation_content(block_key: str, updated_content: str, language: str):
    """
    use this function from the add and update "Website Page Block Translation" which is a child table of website page.
    """
    formated_language = format_language_key(language_key=language)
    translation_ids = frappe.get_list(
        "Translation", {"source_text": block_key,
                        "language": ['LIKE', f"{formated_language}%"]})
    if translation_ids:
        for translation_id in translation_ids:
            translation_doc = frappe.get_doc("Translation", translation_id)
            counter = 1
            if counter == 1:
                translation_doc.translated_text = updated_content
                translation_doc.language = formated_language
                translation_doc.save()
                counter += 1
            else:  # delete the repeated records (same key and language)
                translation_doc.delete()
    else:
        new_doc = frappe.new_doc("Translation")
        new_doc.source_text = block_key
        new_doc.translated_text = updated_content
        new_doc.language = formated_language
        new_doc.insert()


def delete_translation_record(block_key: str, language: str):
    formated_language = format_language_key(language_key=language)
    translation_ids = frappe.get_list("Translation",
                                      filters={"source_text": block_key,
                                               "language": ['LIKE', f"{formated_language}%"]})

    for translation_id in translation_ids:
        translation_doc = frappe.get_doc("Translation", translation_id)
        # Delete the translation record
        translation_doc.delete()
        frappe.db.commit()


def delete_translation_records(block_key: str):
    translation_ids = frappe.get_list("Translation",
                                      filters={"source_text": block_key})

    for translation_id in translation_ids:
        translation_doc = frappe.get_doc("Translation", translation_id)
        # Delete the translation record
        translation_doc.delete()
        frappe.db.commit()
