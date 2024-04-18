import shutil
import os


def execute():
    folders_to_remove = ['../apps/ojeedoo_app/ojeedoo_app/ojeedoo_app/page/translation_page',
                         '../apps/pif_app/pif_app/pay_it_forward/page/translation_page']

    for folder in folders_to_remove:
        try:
            full_path = os.path.join(os.getcwd(), folder)

            if os.path.exists(full_path):
                shutil.rmtree(full_path)
                print(f"Removed {full_path}")
            else:
                print(f"{folder} not found")
        except Exception as e:
            print(f"Error occurred while removing {folder}: {e}")
