#!/usr/bin/env python
import sys
import os
import PySimpleGUI as sg
from box import Box

data = {
    "children": [
        {
            "patient_id": "23123",
            "patient_name": "frank",
            "children": [
                {
                    "study_id": "51212132131231313",
                    "children": [{"series_id": "series_1"}, {"series_id": "series_2"}],
                },
                {
                    "study_id": "9022",
                    "children": [{"series_id": "series_3"}, {"series_id": "series_4"},],
                },
            ],
        },
        {
            "patient_id": "78812",
            "patient_name": "frankzhang",
            "children": [
                {
                    "study_id": "51213098080123123",
                    "children": [{"series_id": "series_1"}, {"series_id": "series_2"}],
                },
                {
                    "study_id": "9022",
                    "children": [{"series_id": "series_3"}, {"series_id": "series_4"},],
                },
            ],
        },
    ]
}

data_box = Box(data)

treedata = sg.TreeData()

treedata.Insert("", "patient", "patient", [])
for patient in data_box.children:
    treedata.Insert(
        "patient",
        patient.patient_id,
        patient.patient_id,
        [patient.patient_id, patient.patient_name],
    )

    treedata.Insert(patient.patient_id, "study", "study", [])

    for study in patient.children:
        treedata.Insert("study", study.study_id, study.study_id, [study.study_id])

        treedata.Insert(study.study_id, "series", "series", [])

        for series in study.children:
            treedata.Insert(
                "series", series.series_id, series.series_id, [series.series_id]
            )

layout = [
    [sg.Text("Tree View")],
    [
        sg.Tree(
            data=treedata,
            headings=["c1", "c2", "c3"],
            auto_size_columns=True,
            num_rows=20,
            col0_width=40,
            key="-TREE-",
            show_expanded=False,
            enable_events=True,
        ),
    ],
    [sg.Button("Ok"), sg.Button("Cancel")],
]

window = sg.Window("Tree Element Test", layout, size=(800, 600))

# Event Loop
while True:
    event, values = window.read()
    if event in (None, "Cancel"):
        break
    print(event, values)
window.close()
