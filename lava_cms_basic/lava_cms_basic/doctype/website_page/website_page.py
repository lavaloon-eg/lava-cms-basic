# Copyright (c) 2024, lavaloon and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document
from lava_cms_basic.patches._2024_4_12_migrate_translation_records import migrate_translation_data


class WebsitePage(Document):
    def validate(self):
        pass
