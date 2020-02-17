#!/usr/bin/env python
import sys
import os
import PySimpleGUI as sg

from folder_reader import read_dicomfolder


treedata = sg.TreeData()


def dicomfolder_to_treedata(dicomfolder, treedata):
    treedata.Insert("", "patient", "patient", [])

    for patient in dicomfolder.children:
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
                treedata.Insert("series", series_uid, series_text, [1, 2, 3])

                # TODO: no need to to show instances
                for instance in series.children:
                    filepath = instance.filepath
                    instance_uid = instance.SOPInstanceUID
                    instance_number = instance.InstanceNumber
                    image_position = instance.ImagePosition
                    image_orientation = instance.ImageOrientation
                    treedata.Insert(series_uid, instance_uid, instance_uid, [filepath])


right_click_menu = ["that", ["View", "there", "those"]]

layout = [
    # Source Folder
    [sg.T("Source Folder")],
    [sg.In(key="source_folder")],
    [sg.FolderBrowse(target="source_folder"), sg.Button("Scan")],
    # Tree View
    [sg.Text("Tree View")],
    [
        sg.Tree(
            data=treedata,
            headings=["file",],
            col_widths=[200, 200],
            max_col_width=300,
            auto_size_columns=True,
            num_rows=20,
            col0_width=80,
            key="_TREE_",
            show_expanded=False,
            enable_events=True,
            right_click_menu=right_click_menu,
        ),
    ],
    [sg.Button("View")],
    # [sg.Button("Ok"), sg.Button("Cancel")],
]

window = sg.Window("Tree Element Test", layout, size=(1000, 800))

# Event Loop
while True:
    event, values = window.read()

    if event == None:  # quit app
        break

    print(">", event, values)

    if event == "Scan":
        if not values["source_folder"]:
            sg.Popup("Error", f"please select a folder to scan!")
            continue

        # clear old data
        del treedata
        treedata = sg.TreeData()

        dicomfolder = read_dicomfolder(values["source_folder"])
        dicomfolder_to_treedata(dicomfolder, treedata)
        window.Element("_TREE_").Update(values=treedata)

    if event == "View":
        if len(values["_TREE_"]) < 1:
            sg.Popup("Error", f"please choose a series to view!")
            continue

        key = values["_TREE_"][0]
        node = treedata.tree_dict[key]
        print(dir(node))
        if node.parent == "series":
            # TODO: we should not rely on `treedata`'s data to business logic
            # we do need a reference to the series in `dicomfolder`
            # possibly via UID lookup? or can be add user data to `node`
            print(f"view series {node.key} of total {len(node.children)} instances")
            vals = []
            for instance in node.children:
                print(instance.values)
                vals.append(instance.values)
            sg.Popup(event, vals)
        else:
            sg.Popup("Error", f"please choose a series to view!")
        pass

window.close()
