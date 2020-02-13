# Create hiracchical treeview Application
from tkinter import *
from tkinter import ttk

app = Tk()
# App Title
app.title("Python GUI Application ")
# Lable
ttk.Label(app, text="Hierachical Treeview").pack()
# Treeview
treeview = ttk.Treeview(app)
treeview.pack()
# Treeview items
treeview.insert("", "0", "item1", text="Parent tree")
treeview.insert("", "1", "item2", text="1st Child")
treeview.insert("", "end", "item3", text="2nd Child")
treeview.insert("item2", "end", "A", text="A")
treeview.insert("item2", "end", "B", text="B")
treeview.insert("item2", "end", "C", text="C")
treeview.insert("item3", "end", "D", text="D")
treeview.insert("item3", "end", "E", text="E")
treeview.insert("item3", "end", "F", text="F")
treeview.move("item2", "item1", "end")
treeview.move("item3", "item1", "end")
# Calling Main()
app.mainloop()
