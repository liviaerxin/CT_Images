#!/usr/bin/env python
import sys
import os
import PySimpleGUI as sg

from folder_reader import read_dicomfolder

"""
    Both window and window_viewer can be active at the same time:
    There are three important things to be mentioned about the design pattern:
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
                series_text = f"{series_uid}"  # f"{series_uid} ({len(series.children)} instances)"
                all_instances = series.children
                treedata.Insert(
                    "series", series_uid, series_text, [len(all_instances), series]
                )

                # no need to to show instances
                # for instance in series.children:
                #     filepath = instance.filepath
                #     instance_uid = instance.SOPInstanceUID
                #     instance_number = instance.InstanceNumber
                #     image_position = instance.ImagePosition
                #     image_orientation = instance.ImageOrientation
                #     treedata.Insert(series_uid, instance_uid, instance_uid, [filepath])
    return treedata


right_click_menu = ["that", ["View", "there", "those"]]

# Window Layout
layout = [
    # Source Folder
    [sg.Text("Source Folder")],
    [sg.InputText(key="_SOURCE_FOLDER_", enable_events=True)],
    [sg.FolderBrowse(button_text="Scan", target="_SOURCE_FOLDER_")],
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
            # right_click_menu=right_click_menu, # there are bugs in MacOS, using `binding-tkiner-events` instead.
        ),
    ],
    [sg.Button("View")],
    # [sg.Button("Ok"), sg.Button("Cancel")],
]

window = sg.Window("Tree Element Test", layout, size=(1000, 800), finalize=True)

# Custom Binding
# (tkinter "events"), seeing: https://pysimplegui.readthedocs.io/en/latest/#binding-tkiner-events
window["_TREE_"].bind("<Double-Button-1>", "+DOUBLE_CLICK+")  # Double Click On Tree Row

if sys.platform == "darwin":
    # Mac OSX
    window["_TREE_"].bind("<Button-2>", "+RIGHT_CLICK+")
else:
    window["_TREE_"].bind("<Button-3>", "+RIGHT_CLICK+")


window_viewer_active = False


# Event Loop
while True:
    # print("reading window")
    event, values = window.read(timeout=100)
    if event != sg.TIMEOUT_KEY:
        print(">window", event, values)  # debug print

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
    ):  # View: choose one series to lanch a viewer window

        if window_viewer_active:
            sg.Popup("Error", f"please close the exsiting viewer window")
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
            number_instances = node.values[0]
            series = node.values[1]
            print(f"view series {node.key} of total {number_instances} instances")

            # vals = []
            # for instance in series.children:
            #     print(instance)
            #     vals.append(instance)
            sg.Popup(event, series)

            # TODO: 2. run algorithm if no cached analysis result for the series
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

            # TODO: 3. open a DICOM viewer window
            # TODO: decouple the code better
            window_viewer_active = True

            layout_viewer = [
                [sg.Text("Viewer")],
                [
                    sg.Graph(
                        canvas_size=(400, 400),
                        graph_bottom_left=(0, 0),
                        graph_top_right=(400, 400),
                        background_color="red",
                        key="graph",
                    )
                ],
                [
                    sg.T("Change circle color to:"),
                    sg.Button("Red"),
                    sg.Button("Blue"),
                    sg.Button("Move"),
                ],
            ]

            window_viewer = sg.Window("Viewer", layout_viewer, finalize=True)

            graph = window_viewer["graph"]
            circle = graph.DrawCircle(
                (75, 75), 25, fill_color="black", line_color="white"
            )
            point = graph.DrawPoint((75, 75), 10, color="green")
            oval = graph.DrawOval(
                (25, 300), (100, 280), fill_color="purple", line_color="purple"
            )
            rectangle = graph.DrawRectangle((25, 300), (100, 280), line_color="purple")
            line = graph.DrawLine((0, 0), (100, 100))

        else:
            sg.Popup("Error", f"please choose a series to view!")
            continue
    else:
        pass

    # Catch window_viewer `event`
    if window_viewer_active:
        # print("reading window_viewer")
        event, values = window_viewer.read(timeout=100)

        if event != sg.TIMEOUT_KEY:
            print(">window_viewer ", event, values)  # debug print

        if event in (None, "Exit"):
            print("Closing window_viewer", event)
            window_viewer_active = False
            window_viewer.close()

        if event is "Blue":
            graph.TKCanvas.itemconfig(circle, fill="Blue")
        elif event is "Red":
            graph.TKCanvas.itemconfig(circle, fill="Red")
        elif event is "Move":
            graph.MoveFigure(point, 10, 10)
            graph.MoveFigure(circle, 10, 10)
            graph.MoveFigure(oval, 10, 10)
            graph.MoveFigure(rectangle, 10, 10)
        else:
            pass


window.close()
del window
