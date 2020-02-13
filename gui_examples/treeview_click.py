import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.tree = ttk.Treeview()
        self.tree.pack()
        for i in range(10):
            self.tree.insert("", "end", text="Item %s" % i)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-2>", self.on_right_click)
        self.tree.bind("<Button-3>", self.on_right_click)
        self.root.mainloop()

    def on_double_click(self, event):
        """action in event of button 1 on tree view"""
        item = self.tree.identify("item", event.x, event.y)
        print("you clicked on", self.tree.item(item, "text"))

    def on_right_click(self, event):
        """action in event of button 3 on tree view"""
        # select row under mouse
        print("hello!")

        def hello():
            print("hello!")

        # create a popup menu
        print(event.x, event.y)
        rowID = self.tree.identify("item", event.x, event.y)
        if rowID:
            self.tree.selection_set(rowID)
            self.tree.focus_set()
            self.tree.focus(rowID)
            print(rowID)

            menu = Menu(self.root, tearoff=0)
            menu.add_command(label="Undo", command=hello)
            menu.add_command(label="Redo", command=hello)
            menu.post(event.x_root, event.y_root)
        else:
            pass


if __name__ == "__main__":
    app = App()
