import webview
import os
import sys

def resource_path(relative_path):
    """
    Get absolute path to resource.
    Works for both development and PyInstaller onefile.
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

html_path = resource_path("index.html")

webview.create_window(
    "My Desktop App",
    html_path,
    width=900,
    height=600
)

webview.start()
