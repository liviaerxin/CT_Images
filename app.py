#!/usr/bin/env python
import sys
import os
import PySimpleGUI as sg

from folder_reader import read_dicomfolder
from viewer import Viewer

"""
Both window and window_viewer can be active at the same time.
There are three important things to be mentioned about this design pattern:
1. The layout for window_viewer must be fresh every time the window_viewer is created
2. Both windows must have a read timeout to make themself non-blocking for keeping them active at the `same` time
3. There is a safeguard policy to stop from launching multiple copies of window_viewer.  Only 1 window_viewer is visible at a time
"""


treedata = sg.TreeData()


def mock_run_algorithm():
    print(f"start running algorithm")
    count = 100
    for i in range(count):
        print(f"run {i}")
        progress = i / count * 100
        yield progress
    print(f"end running algorithm")


def dicomfolder_to_treedata(dicomfolder):
    treedata = sg.TreeData()
    treedata.Insert("", "patient", "patient", [])

    for patient in dicomfolder.patient_records:
        patient_id = patient.PatientID
        patient_name = patient.PatientName
        treedata.Insert(
            "patient", patient_id, patient_id, [],
        )

        treedata.Insert(patient_id, "study", "study", [])

        for study in patient.children:
            study_uid = study.StudyInstanceUID
            study_id = study.StudyID
            study_date = study.StudyDate
            study_description = study.StudyDescription
            treedata.Insert("study", study_uid, study_uid, [])

            treedata.Insert(study_uid, "series", "series", [])

            for series in study.children:
                series_uid = series.SeriesInstanceUID
                modality = series.Modality
                series_number = series.SeriesNumber
                series_description = series.SeriesDescription
                series_text = f"{series_uid} ({len(series.children)} instances)"
                treedata.Insert("series", series_uid, series_text, [series])
    return treedata


right_click_menu = ["that", ["View", "there", "those"]]

# Window Layout
layout = [
    # Source Folder
    [sg.Text("Source Folder")],
    [
        sg.InputText(key="_SOURCE_FOLDER_", enable_events=True),
        sg.FolderBrowse(button_text="Scan", target="_SOURCE_FOLDER_"),
    ],
    # Tree View
    [sg.Text("Tree View")],
    [
        sg.Tree(
            data=treedata,
            headings=["number of instances",],
            visible_column_map=[True,],
            col_widths=[200, 200],
            max_col_width=300,
            auto_size_columns=True,
            num_rows=20,
            col0_width=80,
            key="_TREE_",
            show_expanded=False,
            justification="center",
            enable_events=True,
            visible=True,
            # there are bugs in MacOS, use custom binding instead.
            # right_click_menu=right_click_menu,
        ),
    ],
    [sg.Button("View")],
]

window = sg.Window("DICOM Folder Tree View", layout, size=(1000, 800), finalize=True)

# Custom Binding
# (tkinter "events"), seeing: https://pysimplegui.readthedocs.io/en/latest/#binding-tkiner-events
# Double Click On Tree Row
window["_TREE_"].bind("<Double-Button-1>", "+DOUBLE_CLICK+")

# right click, different for OSX
if sys.platform == "darwin":
    # Mac OSX
    window["_TREE_"].bind("<Button-2>", "+RIGHT_CLICK+")
else:
    window["_TREE_"].bind("<Button-3>", "+RIGHT_CLICK+")


window_viewer = None

# Event Loop
while True:
    # print("reading window")
    event, values = window.read(timeout=100)
    if event != sg.TIMEOUT_KEY:
        print("> window", event, values)  # debug print

    if event in (None, "Quit"):  # quit app
        break

    # Catch window `event`
    if event == "_SOURCE_FOLDER_":  # Scan: choose dicom folder to scan
        if not values["_SOURCE_FOLDER_"]:
            sg.Popup("Error", f"please select a folder to scan!")
            continue

        # Do `Scan` job
        sg.OneLineProgressMeter(
            "Scanning DICOM Folder", 0, 2, "_SCAN_METER_", "Scan...", orientation="h"
        )
        dicomfolder = read_dicomfolder(values["_SOURCE_FOLDER_"])

        sg.OneLineProgressMeter(
            "Scanning DICOM Folder", 1, 2, "_SCAN_METER_", "Scan...", orientation="h"
        )
        treedata = dicomfolder_to_treedata(dicomfolder)

        sg.OneLineProgressMeter(
            "Scanning DICOM Folder", 2, 2, "_SCAN_METER_", "Scan...", orientation="h"
        )

        window["_TREE_"].update(values=treedata)

    elif event in (
        "View",
        "_TREE_+DOUBLE_CLICK+",
    ):  # View: choose one series to launch a viewer window
        if window_viewer:
            sg.Popup("Error", f"please close the existing viewer window")
            continue

        if len(values["_TREE_"]) < 1:
            sg.Popup("Error", f"please choose a series to view!")
            continue

        if len(values["_TREE_"]) > 1:
            sg.Popup("Error", f"Don't choose multiple series to view!")
            continue

        key = values["_TREE_"][0]
        node = treedata.tree_dict[key]
        print(dir(node))
        if node.parent == "series":
            # 1. get series data
            # we should not rely on `treedata`'s data to business logic
            # we do add `series` data to `node` and can directly retrive it from the values of `node`, so the data structure is based on our defined `Series`
            series = node.values[0]
            instances = series.children
            print(f"view series {node.key} of total {len(instances)} instances")

            # TODO: run algorithm if no cached analysis result for the series
            for progress in mock_run_algorithm():  # progress is from 0 to 100
                sg.OneLineProgressMeter(
                    "Analyzing the series",
                    int(progress),
                    100,
                    "_ANALYZE_METER_",
                    "Analyzing...",
                    orientation="h",
                )

                pass
            sg.OneLineProgressMeterCancel("_ANALYZE_METER_")

            # open a DICOM viewer window
            window_viewer = Viewer(series, instances)
        else:
            # sg.Popup("Error", f"please choose a series to view!")
            continue
    else:
        pass

    # handle Viewer's event
    if window_viewer:
        ret = window_viewer.event_handler()

        if ret is None:
            # Viewer is closed
            window_viewer = None


window.close()
del window
