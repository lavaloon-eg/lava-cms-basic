import json
import frappe


def execute():
    """"Add "lava-cms-basic"'s Workspace"""
    print(f"Patch: _2024_4_12_create_lava_cms_basic_workspace started")
    _add_lava_cms_basic_workspace()
    print(f"Patch: _2024_4_12_create_lava_cms_basic_workspace finished")


def _add_lava_cms_basic_workspace():
    workspace_title = "Lava CMS Basic"    # will be used as its ID as well
    if frappe.db.exists("Workspace", workspace_title):
        print(f"Workspace {workspace_title} already exists")
    else:
        shortcuts = [
            {
                "doc_view": "List",
                "label": "Website Page",
                "link_to": "Website Page",
                "doctype": "DocType"
            },
            {
                "doc_view": "List",
                "label": "Website Page Block",
                "link_to": "Website Page Block",
                "doctype": "DocType"
            }
        ]
        roles = [
            {
                "role": "System Manager"
            }
        ]

        try:
            content = []
            workspace_doc = frappe.new_doc("Workspace")
            workspace_doc.name = workspace_title
            workspace_doc.label = workspace_title
            workspace_doc.title = workspace_title
            workspace_doc.sequence_id = 1
            workspace_doc.public = 1
            workspace_doc.is_standard = 1
            workspace_doc.module = "Lava Cms Basic"
            for shortcut in shortcuts:
                workspace_doc.append("shortcuts", {
                    "doctype": shortcut["doctype"],
                    "label": shortcut["label"],
                    "link_to": shortcut["link_to"],
                    "doc_view": shortcut["doc_view"]
                })
                content.append({"type": "shortcut", "data": {"shortcut_name": shortcut["label"], "col": 4}})
            for role in roles:
                workspace_doc.append("roles", {
                    "role": role["role"]
                })

            workspace_doc.content = json.dumps(content)
            workspace_doc.insert(ignore_permissions=True)
            print(f"Workspace {workspace_title} added successfully")
        except Exception as e:
            print(f"Error adding Workspace {workspace_title}: {e}")
