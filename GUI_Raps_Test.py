import tkinter as tk

window = tk.Tk()
# to rename the title of the window
window.title("GUI")
# pack is used to show the object in the window
label = tk.Label(window, text = "Welcome to DataCamp's Tutorial on Tkinter!").pack()
window.mainloop()