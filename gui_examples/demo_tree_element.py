#!/usr/bin/env python
import sys
import os
from PIL import (
    ImageTk,
    Image,
)  # on macOS: _tkinter.TclError: couldn't recognize data in image file https://github.com/PySimpleGUI/PySimpleGUI/issues/1369

import PySimpleGUI as sg

"""
    A PySimpleGUI or PySimpleGUIQt demo program that will display a folder heirarchy with icons for the folders and files.
    Note that if you are scanning a large folder then tkinter will eventually complain abouit too many bitmaps and crash
    Getting events back from clicks on the entries works for PySimpleGUI, but appears to not be implemented in PySimpleGUIQt
    If you need tree events using PySimpleGUIQt then post an Issue on the GitHub http://www.PySimpleGUI.com
"""

# Base64 versions of images of a folder and a file. PNG files (may not work with PySimpleGUI27, swap with GIFs)

folder_icon = "./folder.gif"
file_icon = "./file.gif"

starting_path = sg.popup_get_folder("Folder to display")

if not starting_path:
    print("not starting_path")
    sys.exit(0)

print(f"starting_path: {starting_path}")

treedata = sg.TreeData()


def add_files_in_folder(parent, dirname):
    print("add_files_in_folder")
    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f)
        if os.path.isdir(fullname):  # if it's a folder, add folder and recurse
            treedata.Insert(parent, fullname, f, values=[], icon=folder_icon)
            add_files_in_folder(fullname, fullname)
        else:

            treedata.Insert(
                parent, fullname, f, values=[os.stat(fullname).st_size], icon=file_icon
            )


add_files_in_folder("", starting_path)

layout = [
    [sg.Text("File and folder browser Test")],
    [
        sg.Tree(
            data=treedata,
            headings=["Size",],
            auto_size_columns=True,
            num_rows=20,
            col0_width=30,
            key="-TREE-",
            show_expanded=False,
            enable_events=True,
        ),
    ],
    [sg.Button("Ok"), sg.Button("Cancel")],
]

window = sg.Window("Tree Element Test", layout)

while True:  # Event Loop
    event, values = window.read()
    if event in (None, "Cancel"):
        break
    print(event, values)
window.close()
