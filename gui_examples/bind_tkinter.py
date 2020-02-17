import PySimpleGUI as sg

sg.theme('Dark Green 2')

layout = [  [sg.Text('My Window')],
            [sg.Input(key='-IN-'), sg.Text(size=(15,1), key='-OUT-')],
            [sg.Button('Go'), sg.Button('Exit')]
              ]

window = sg.Window('Window Title', layout, finalize=True)

window['-IN-'].bind("<FocusIn>", '+FOCUS+')
window.bind("<Button-1>", 'Window Click')
window['Go'].bind("<Button-3>", '+RIGHT CLICK+')

while True:             # Event Loop
    event, values = window.read()
    print(event, values)
    if event in (None, 'Exit'):
        break

window.close(); del window