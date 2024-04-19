import frappe


def execute():
    try:
        patch_name = ""
        print(f"Run patch '{patch_name}'")
        records = frappe.db.sql("SELECT name FROM `tabDocType` WHERE name='Website Page Block'")
        if not records:
            sql = """delete from `tabDocType` where name ='Website Page';
                    delete from `tabModule Def` where name = 'Lava Cms Basic';
                    """
            frappe.db.sql(sql)
            frappe.db.commit()
            print("Patch finished: 'Lava Cms Basic' and 'Website Page' were deleted successfully")
    except Exception as e:
        print("Exception was occurred while trying to delete from DB,"
              " 'Lava Cms Basic' and 'Website Page'" + str(e))
