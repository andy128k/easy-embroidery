from Tkinter import *

def gui(elements):
    master = Tk()
    w = Canvas(master, width=600, height=600)
    w.pack()

    for e in elements:
        prev = None
        for p in e.points(2, 1):
            if prev:
                w.create_line(2 * prev[0], 2 * prev[1], 2 * p[0], 2 * p[1])
            prev = p

    mainloop()

