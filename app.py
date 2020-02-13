#!/usr/bin/env python
import sys
import os
import PySimpleGUI as sg

from create_simple_DICOMDIR import create_simple_DICOMDIR


treedata = sg.TreeData()

def add_DICOMDIR_to_tree(dicomdir):
    print("add_DICOMDIR_to_tree")

    treedata.Insert("", "patient", "patient", [])

    for patient in dicomdir.children:
        patient_id = patient.PatientID
        patient_name = patient.PatientName
        treedata.Insert(
            "patient",
            patient_id,
            patient_id,
            [],
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
                treedata.Insert(
                    "series", series_uid, series_uid, []
                )

                #treedata.Insert(series_uid, "instance", "instance", [])

                for instance in series.children:
                    filepath = instance.filepath
                    instance_uid = instance.SOPInstanceUID
                    instance_number = instance.InstanceNumber
                    image_position = instance.ImagePosition
                    image_orientation = instance.ImageOrientation
                    treedata.Insert(
                        series_uid, instance_uid, instance_uid, [filepath]
                    )

right_click_menu = ['that', ['Run', 'there', 'those']]

layout = [
    # Source Folder
[sg.T('Source Folder')],
              [sg.In(key='source_folder')],
              [sg.FolderBrowse(target='source_folder'), sg.Button("Organize")],

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
        ),
    ],
    [sg.Button("Run")],
    [sg.Button("Ok"), sg.Button("Cancel")],
]

window = sg.Window("Tree Element Test", layout, size=(1000, 800))

# Event Loop
while True:
    event, values = window.read()
    
    if event in (None, "Cancel"):
        break
    
    print(event, values)
    
    if event == "Organize":
        del treedata
        treedata = sg.TreeData()
        source_folder = values["source_folder"]
        dicomdir = create_simple_DICOMDIR(source_folder)
        add_DICOMDIR_to_tree(dicomdir)
        print(window.Element("_TREE_").Update(values=treedata))


    if event == "Run":
        if len(values["_TREE_"]) < 1:
            sg.Popup("Message", f"please choose a series to run!")
            continue
        key = values["_TREE_"][0]
        node = treedata.tree_dict[key]
        print(dir(node))
        if node.parent == "series":
            print(f"run series {node.key} of total {len(node.children)} instances")
            vals = []
            for instance in node.children:
                print(instance.values)
                vals.append(instance.values)
            sg.Popup(event, vals)
        else:
            print(f"please choose a series to run!")
            sg.Popup("Message", f"please choose a series to run!")
        pass

window.close()