# Copyright (c) 2024, lavaloon and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document
from lava_cms_basic.utils.localization import *


class WebsitePageBlock(Document):
    def validate(self):
        translation_records = self.get('translations')
        languages = []
        for translation_record in translation_records:
            if translation_record.language not in languages:
                languages.append(translation_record.language)
            else:
                frappe.throw(msg="Cannot repeat the language")

    def on_update(self):
        try:
            # check the child table records to identify the deleted records
            old_doc = self.get_doc_before_save()
            old_translation_records = None
            translation_records = self.get('translations')
            if old_doc:
                old_translation_records = self.get('translations')
                for old_translation_record in old_translation_records:
                    is_deleted = True
                    for new_translation_record in old_translation_records:
                        if old_translation_record.language == new_translation_record.language:
                            is_deleted = False
                    if is_deleted:
                        delete_translation_record(block_key=self.block_key,
                                                  language=old_translation_record.language)
            # update the standard translation
            for translation_record in translation_records:
                add_update_translation_content(block_key=self.block_key,
                                               updated_content=translation_record.content,
                                               language=translation_record.language)
        except Exception as ex:
            frappe.msgprint(f'Cannot save the data because of the error: {str(ex)}')

    def on_trash(self):
        delete_translation_records(block_key=self.block_key)