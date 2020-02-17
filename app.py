#!/usr/bin/env python
import sys
import os
import PySimpleGUI as sg

from folder_reader import read_dicomfolder

treedata = sg.TreeData()


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

                # TODO: no need to to show instances
                # for instance in series.children:
                #     filepath = instance.filepath
                #     instance_uid = instance.SOPInstanceUID
                #     instance_number = instance.InstanceNumber
                #     image_position = instance.ImagePosition
                #     image_orientation = instance.ImageOrientation
                #     treedata.Insert(series_uid, instance_uid, instance_uid, [filepath])
    return treedata


right_click_menu = ["that", ["View", "there", "those"]]

layout = [
    # Source Folder
    [sg.Text("Source Folder")],
    [sg.InputText(key="_SOURCE_FOLDER_", enable_events=True)],
    [
        sg.FolderBrowse(
            button_text="Browse", target="_SOURCE_FOLDER_"
        )
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
            #right_click_menu=right_click_menu, # there are bugs in MacOS, using `binding-tkiner-events` instead.
        ),
    ],
    [sg.Button("View")],
    # [sg.Button("Ok"), sg.Button("Cancel")],
]

window = sg.Window("Tree Element Test", layout, size=(1000, 800), finalize=True)

# Custom Element Event Binding(tkinter "events"), seeing: https://pysimplegui.readthedocs.io/en/latest/#binding-tkiner-events 
window["_TREE_"].bind("<Double-Button-1>", "+DOUBLE_CLICK+") # Double Click On Tree Row

if sys.platform == "darwin":
    # Mac OSX
    window["_TREE_"].bind("<Button-2>", "+RIGHT_CLICK+")
else:
    window["_TREE_"].bind("<Button-3>", "+RIGHT_CLICK+")


# Event Loop
while True:
    event, values = window.read()
    print(">", event, values)  # debug print

    if event in (None, "Quit"):  # quit app
        break

    if event == "_SOURCE_FOLDER_":  # choose dicom folder to scan
        if not values["_SOURCE_FOLDER_"]:
            sg.Popup("Error", f"please select a folder to scan!")
            continue

        # clear old data
        # del treedata

        dicomfolder = read_dicomfolder(values["_SOURCE_FOLDER_"])
        treedata = dicomfolder_to_treedata(dicomfolder)
        window["_TREE_"].update(values=treedata)

    elif event in ("View", "_TREE_+DOUBLE_CLICK+"): # choose one series to view
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
        else:
            sg.Popup("Error", f"please choose a series to view!")
    else:
        pass

window.close()
