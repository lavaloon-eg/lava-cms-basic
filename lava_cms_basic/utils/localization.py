import frappe


@frappe.whitelist()
def format_language_key(language_key, default_language_key: str = 'ar'):
    """
    set the session language of the user. The method identifies the language based on
    the first 2 letters lower case. If not en (English), this means ar (Arabic)
    """
    if len(language_key) < 2:
        frappe.throw(msg="the language key's length must be >=2 characters",
                     exc=ValueError)
    selected_language = default_language_key
    if language_key[:2].lower() == "en":
        selected_language = "en"
    return selected_language


@frappe.whitelist()
def get_page_content_list(page_id):
    if not page_id:
        frappe.msgprint('Make sure of selecting an existing page')
        return

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
                b.page = '{page_id}'
            ORDER BY b.title, b.block_key, t.language
            """
    records = frappe.db.sql(sql, as_dict=1)
    return records


def migrate_translation_data():
    sql = f"""
            SELECT source_text, language, translated_text
            FROM `tabTranslation`
            WHERE source_text LIKE '%-section-%'
            ORDER BY source_text, language
            """
    translation_records = frappe.db.sql(sql, as_dict=1)
    for translation_record in translation_records:
        block_key = translation_record.source_text
        keys = block_key.split("-")
        page_title = keys[0]
        block_title = block_key.replace(f"{page_title}-", "")
        page_id = add_page_if_not_exist(page_title=page_title)
        add_block_and_translation_if_not_exist(page_id=page_id, block_title=block_title, block_key=block_key,
                                               language=translation_record.language,
                                               translated_text=translation_record.translated_text)


def add_page_if_not_exist(page_title: str):
    """
    add the page if not exist, and return the page id if new or already exist
    this function is use for the data migration only
    """
    page_id = frappe.get_value("Website Page", "name", {"title": page_title})
    if page_id:
        return page_id
    else:
        new_doc = frappe.new_doc("Website Page")
        new_doc.title = page_title
        new_doc.insert()
        return new_doc.name


def add_block_and_translation_if_not_exist(page_id: str, block_title: str, block_key: str,
                                           language: str, translated_text: str):
    """
    add the block if not exist, and return the block id if new or already exist.
    this function is used for the data migration only.
    """
    block_id = frappe.get_value("Website Page Block", "name", {"block_key": block_key})
    block_doc = None
    if not block_id:
        new_doc = frappe.new_doc("Website Page Block")
        new_doc.title = block_title
        new_doc.page = page_id
        new_doc.block_key = block_key
        new_doc.insert()
        block_doc = new_doc
        block_id = new_doc.name

    formated_language = format_language_key(language_key=language)
    translation_id = frappe.get_value("Website Page Block Translation", "name", {
        "block_key": block_key,
        "language": formated_language
    })
    if not translation_id:
        block_doc.append("translations", {
            "website_page_block": block_id,
            "page": page_id,
            "block_key": block_key,
            "language": formated_language,
            "content": translated_text
        })
        block_doc.save()


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
