import PySimpleGUI as sg

def right_click(self, event):
    # don't care here, maybe it still not working
    self.event_generate('<Button-3>', x=event.x, y=event.y)
    return 'break'

layout = [[sg.Button('Test', key='BTTN')]]
window = sg.Window('Test', layout=layout).finalize()

window['BTTN'].Widget.bind('<Button-2>', right_click)

while True:

    event, values = window.read()
    print(event, values)

    if event == None:
        break

window.close()