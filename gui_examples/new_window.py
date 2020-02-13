import sys

if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg

layout = [
    [sg.Text("Your typed chars appear here:"), sg.Text("", key="_OUTPUT_")],
    [sg.Input(do_not_clear=True, key="_IN_")],
    [sg.Button("Show"), sg.Button("Exit")],
]

window = sg.Window("Window Title").Layout(layout)

while True:  # Event Loop
    event, values = window.Read()
    print(event, values)
    if event is None or event == "Exit":
        break
    if event == "Show":
        layout2 = [
            [sg.Text("The second window"), sg.Text("", key="_OUTPUT_")],
            [sg.Input(do_not_clear=True, key="_IN_")],
            [sg.Button("Show"), sg.Button("Exit")],
        ]
        window2 = sg.Window("Second Window").Layout(layout2)

        event, values = window2.Read()
        window2.Close()

window.Close()
