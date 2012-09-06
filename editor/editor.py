import math
from gi.repository import GObject, Gtk, Gdk

class Canvas(Gtk.Layout):
    def __init__(self):
        Gtk.Layout.__init__(self)
        self.set_size(1000, 1000)
        self.connect('draw', self.draw)

    def draw(self, widget, cr):
        width = self.get_allocated_width() / 50.0
        height = self.get_allocated_height() / 50.0

        cr.scale(50, 50)

        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.set_line_width(0.01)
        for x in xrange(1, int(math.ceil(width))):
            cr.move_to(x+0.025, 0)
            cr.line_to(x+0.025, height)
            cr.stroke()
        for y in xrange(1, int(math.ceil(height))):
            cr.move_to(0, y+0.025)
            cr.line_to(width, y+0.025)
            cr.stroke()

class CanvasObject(Gtk.DrawingArea):
    def __init__(self, canvas):
        Gtk.DrawingArea.__init__(self)
        self.canvas = canvas
        self.set_size_request(10, 10)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK)
        self.connect('draw', self.draw)
        self.connect('button_press_event', self.button_press_event)
        self.connect('motion_notify_event', self.motion_notify_event)
        self.canvas.put(self, 0, 0)

    def get_int_child_property(self, property_name):
        v = GObject.Value()
        v.init(GObject.TYPE_INT)
        self.canvas.child_get_property(self, property_name, v)
        return v.get_int()

    def get_x(self):
        return self.get_int_child_property('x')

    def get_y(self):
        return self.get_int_child_property('y')

    def set_position(self, x, y):
        self.canvas.move(self, x, y)

    def button_press_event(self, obj, event):
        self.sx = event.x
        self.sy = event.y
        return True

    def motion_notify_event(self, obj, event):
        if event.state & Gdk.ModifierType.BUTTON1_MASK:
            x = self.get_x()
            y = self.get_y()
            dx = event.x - self.sx
            dy = event.y - self.sy
            self.set_position(x + dx, y + dy)
        return True

    def draw(self, widget, cr):
        cr.set_source_rgb(0.8, 0.2, 0.3)
        cr.rectangle(0, 0, 10, 10)
        cr.fill()

class Rectangle(CanvasObject):
    def __init__(self, canvas):
        CanvasObject.__init__(self, canvas)
        self.set_size_request(70, 50)

    def draw(self, widget, cr):
        cr.set_source_rgb(0.8, 0.8, 0.3)
        cr.rectangle(0, 0, 70, 50)
        cr.fill()

class Handle(CanvasObject):
    def __init__(self, canvas):
        CanvasObject.__init__(self, canvas)

    def draw(self, widget, cr):
        cr.set_source_rgb(0.2, 0.8, 0.2)
        cr.rectangle(0, 0, 10, 10)
        cr.fill()
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(0, 0, 10, 10)
        cr.stroke()

class ResizableRectangle(CanvasObject):
    def __init__(self, canvas):
        CanvasObject.__init__(self, canvas)
        self.width = 80
        self.height = 50
        self.set_size_request(self.width, self.height)

        self.width_handle = Handle(canvas)
        self.width_handle_set_position_old = self.width_handle.set_position
        self.width_handle.set_position = self.width_handle_set_position

        self.height_handle = Handle(canvas)
        self.height_handle_set_position_old = self.height_handle.set_position
        self.height_handle.set_position = self.height_handle_set_position

        self.corner_handle = Handle(canvas)
        self.corner_handle_set_position_old = self.corner_handle.set_position
        self.corner_handle.set_position = self.corner_handle_set_position

    def width_handle_set_position(self, hx, hy):
        x = self.get_x()
        y = self.get_y()
        self.width = hx + 5 - x
        if self.width < 0:
            self.width = 0
        self.set_size_request(self.width, self.height)
        self.position_handles()

    def height_handle_set_position(self, hx, hy):
        x = self.get_x()
        y = self.get_y()
        self.height = hy + 5 - y
        if self.height < 0:
            self.height = 0
        self.set_size_request(self.width, self.height)
        self.position_handles()

    def corner_handle_set_position(self, hx, hy):
        x = self.get_x()
        y = self.get_y()
        self.width = hx + 5 - x
        self.height = hy + 5 - y
        if self.width < 0:
            self.width = 0
        if self.height < 0:
            self.height = 0
        self.set_size_request(self.width, self.height)
        self.position_handles()

    def set_position(self, x, y):
        super(ResizableRectangle, self).set_position(x, y)
        self.position_handles()

    def position_handles(self):
        x = self.get_x()
        y = self.get_y()
        self.width_handle_set_position_old(x + self.width - 5, y + (self.height - 5) / 2)
        self.height_handle_set_position_old(x + (self.width - 5) / 2, y + self.height - 5)
        self.corner_handle_set_position_old(x + self.width - 5, y + self.height - 5)

    def draw(self, widget, cr):
        cr.set_line_width(1)
        cr.set_source_rgb(0.2, 0.2, 0.3)
        cr.rectangle(0.5, 0.5, int(self.width) - 0.5, int(self.height) - 0.5)
        cr.stroke()

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.set_size_request(800, 600)

        hbox = Gtk.HBox()
        self.add(hbox)

        buttons = Gtk.VBox(False, 10)
        hbox.pack_start(buttons, False, True, 10)

        buttons.pack_start(Gtk.Button(label="Button #1"), False, True, 0)
        buttons.pack_start(Gtk.Button(label="Button #2"), False, True, 0)
        buttons.pack_start(Gtk.Button(label="Button #3"), False, True, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        hbox.pack_start(sw, True, True, 0)

        self.canvas = Canvas()
        sw.add(self.canvas)

        r = Rectangle(self.canvas)
        r.set_position(50, 50)

        r = Rectangle(self.canvas)
        r.set_position(250, 50)

        r = Rectangle(self.canvas)
        r.set_position(350, 50)

        r = ResizableRectangle(self.canvas)
        r.set_position(50, 150)

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

