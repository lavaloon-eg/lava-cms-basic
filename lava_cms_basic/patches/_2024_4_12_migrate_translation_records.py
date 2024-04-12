import frappe
from lava_cms_basic.utils.localization import format_language_key


def execute():
    print('patch: migrate_translation_data started')
    migrate_translation_data()
    print('patch: migrate_translation_data completed')


def migrate_translation_data():
    sql = f"""
            SELECT source_text, language, translated_text
            FROM `tabTranslation`
            WHERE source_text LIKE '%-section-%'
            ORDER BY source_text, language
            """
    translation_records = frappe.db.sql(sql, as_dict=1)
    for translation_record in translation_records:
        try:
            block_key = translation_record.source_text
            keys = block_key.split("-")
            page_title = keys[0]
            block_title = block_key.replace(f"{page_title}-", "")
            page_id = _add_page_if_not_exist(page_title=page_title)
            _add_block_and_translation_if_not_exist(page_id=page_id, block_title=block_title, block_key=block_key,
                                                    language=translation_record.language,
                                                    translated_text=translation_record.translated_text)
        except Exception as ex:
            print(f"Error occurred during the patch of translation migration."
                  f" key: {translation_record.source_text}. error: '{str(ex)}'")


def _add_page_if_not_exist(page_title: str):
    """
    add the page if not exist, and return the page id if new or already exist
    this function is use for the data migration only
    """
    page_ids = frappe.get_list("Website Page", filters={"title": page_title})
    if page_ids:
        if len(page_ids) == 1:
            return page_ids[0]
        else:
            frappe.throw(f"There are more {len(page_ids)} with title '{page_title}'")
    else:
        new_doc = frappe.new_doc("Website Page")
        new_doc.title = page_title
        new_doc.save()
        return new_doc.name


def _add_block_and_translation_if_not_exist(page_id: str, block_title: str, block_key: str,
                                            language: str, translated_text: str):
    """
    add the block if not exist, and return the block id if new or already exist.
    this function is used for the data migration only.
    """
    block_ids = frappe.get_list("Website Page Block", filters={"block_key": block_key})
    block_doc = None
    if not block_ids:
        new_doc = frappe.new_doc("Website Page Block")
        new_doc.title = block_title
        new_doc.page = page_id
        new_doc.block_key = block_key
        new_doc.save()
        block_doc = new_doc
    else:
        if len(block_ids) == 1:
            block_doc = frappe.get_doc("Website Page Block", block_ids[0])
        else:
            frappe.throw(msg=f"block key {block_key} has {len(block_ids)} blocks")

    formated_language = format_language_key(language_key=language)
    translation_ids = frappe.get_list("Website Page Block Translation", filters={
        "block_key": block_key,
        "language": formated_language
    })

    if not translation_ids:
        block_doc.append("translations", {
            "website_page_block": block_doc.name,
            "page": page_id,
            "block_key": block_key,
            "language": formated_language,
            "content": translated_text
        })
        block_doc.save()
