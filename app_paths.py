#app_paths.py

import os, sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# def resource_path(relative_path):
#     """ Get absolute path to resource, works for dev and for PyInstaller exe """
#     if hasattr(sys, '_MEIPASS'):
#         return os.path.join(sys._MEIPASS, relative_path)
#     return os.path.join(os.path.abspath("."), relative_path)



# # pyinstaller --onefile --noconsole --name FireDetectionApp --icon=app_icon.ico --add-data "yolov8n.pt;." --add-data "templates;templates" --add-data "static;static" FD_yolo_model.py