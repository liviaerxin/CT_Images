import pprint
import PySimpleGUI as sg


class Viewer:
    def __init__(self, series, instances, analysis=None):
        super().__init__()
        print(pprint.pformat(series))
        self._series = series
        self._instances = instances
        self._analysis = analysis

        layout_viewer = [
            [sg.Text("Viewer")],
            [
                sg.Graph(
                    canvas_size=(600, 600),
                    graph_bottom_left=(0, 0),
                    graph_top_right=(600, 600),
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

        window = self._window = sg.Window("Viewer", layout_viewer, finalize=True)
        graph = self._graph = window["graph"]
        self._items = {
            "circle": graph.DrawCircle(
                (75, 75), 25, fill_color="black", line_color="white"
            ),
            "line": graph.DrawLine((0, 0), (100, 100)),
            "oval": graph.DrawOval(
                (25, 300), (100, 280), fill_color="purple", line_color="purple"
            ),
            "point": graph.DrawPoint((75, 75), 10, color="green"),
            "rectangle": graph.DrawRectangle(
                (25, 300), (100, 280), line_color="purple"
            ),
        }

    def event_handler(self):
        event, values = self._window.read(timeout=100)

        if event == sg.TIMEOUT_KEY:
            return True

        print("> window_viewer ", event, values)  # debug print

        if event in (None, "Exit"):
            print("Closing window_viewer", event)
            self._window.close()
            return None

        graph = self._graph
        circle = self._items["circle"]
        if event == "Blue":
            graph.TKCanvas.itemconfig(circle, fill="Blue")
        elif event == "Red":
            graph.TKCanvas.itemconfig(circle, fill="Red")
        elif event == "Move":
            for item in self._items.values():
                graph.MoveFigure(item, 10, 10)
        else:
            pass

        return True
