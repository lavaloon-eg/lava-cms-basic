import frappe


def execute():
    try:
        if frappe.db.exists("Page", "translation_page"):
            page_doc = frappe.get_doc("Page", "translation_page")
            page_doc.delete()
            print("Translation Page deleted successfully")
    except Exception as e:
        print("Exception was occured while trying to delete Translation Page" + str(e))
