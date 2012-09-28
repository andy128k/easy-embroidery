import math
from gi.repository import GObject, Gtk, Gdk, cairo

class Canvas(Gtk.Layout):
    width = 200 # mm
    height = 200 # mm
    ppm = 5 # points per milimeter
    objects = []

    def pixel_width(self):
        return self.width * self.ppm

    def pixel_height(self):
        return self.width * self.ppm

    def __init__(self):
        Gtk.Layout.__init__(self)
        self.set_size(self.pixel_width(), self.pixel_height())
        self.connect('draw', self.draw)

    def draw(self, widget, cr):
        cr = self.get_bin_window().cairo_create()

        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(0, 0, self.pixel_width(), self.pixel_height())
        cr.fill()

        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.set_line_width(0.5)
        for i in xrange(10, self.width, 10): # step 1 cm
            x = i * self.ppm + 1.25
            cr.move_to(x, 0)
            cr.line_to(x, self.pixel_height())
            cr.stroke()
        for i in xrange(10, self.height, 10): # step 1 cm
            y = i * self.ppm + 1.25
            cr.move_to(0, y)
            cr.line_to(self.pixel_width(), y)
            cr.stroke()

        for obj in self.objects:
            cr.save()
            obj.draw(cr)
            cr.restore()

class Handle(Gtk.DrawingArea):
    def __init__(self, canvas, color=None):
        Gtk.DrawingArea.__init__(self)
        self.canvas = canvas
        self.color = color or (0.2, 0.8, 0.2)
        self.on_move = None
        self.move_disabled = False
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

    def set_position(self, x, y, disable_handler=False):
        if self.move_disabled:
            return
        self.move_disabled = True

        if not disable_handler and self.on_move:
            old_x = self.get_x()
            old_y = self.get_y()
            x, y = self.on_move(old_x, old_y, x, y)

        self.canvas.move(self, x, y)
        self.canvas.queue_draw()

        self.move_disabled = False

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
        cr.set_source_rgb(*self.color)
        cr.rectangle(0, 0, 10, 10)
        cr.fill()
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(0, 0, 10, 10)
        cr.stroke()

class ResizableRectangle(object):
    def __init__(self, canvas, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

        self.position_handle = Handle(canvas, (0.2, 0.2, 0.8))
        self.width_handle = Handle(canvas)
        self.height_handle = Handle(canvas)
        self.corner_handle = Handle(canvas)
        canvas.objects.append(self)

        self.position_handle.on_move = self.position_handle_moved
        self.width_handle.on_move = self.width_handle_moved
        self.height_handle.on_move = self.height_handle_moved
        self.corner_handle.on_move = self.corner_handle_moved

        self.position_handles()

    def position_handle_moved(self, old_x, old_y, hx, hy):
        self.x = hx + 5
        self.y = hy + 5
        self.position_handles()
        return hx, hy

    def width_handle_moved(self, old_x, old_y, hx, hy):
        self.width = hx + 5 - self.x
        if self.width < 0:
            self.width = 0
            hx = old_x
        self.position_handles()
        return hx, old_y

    def height_handle_moved(self, old_x, old_y, hx, hy):
        self.height = hy + 5 - self.y
        if self.height < 0:
            self.height = 0
            hy = old_y
        self.position_handles()
        return old_x, hy

    def corner_handle_moved(self, old_x, old_y, hx, hy):
        self.width = hx + 5 - self.x
        self.height = hy + 5 - self.y
        if self.width < 0:
            self.width = 0
            hx = old_x
        if self.height < 0:
            self.height = 0
            hy = old_y
        self.position_handles()
        return hx, hy

    def position_handles(self):
        self.position_handle.set_position(self.x - 5, self.y - 5, True)
        self.width_handle.set_position(self.x + self.width - 5, self.y + (self.height - 5) / 2, True)
        self.height_handle.set_position(self.x + (self.width - 5) / 2, self.y + self.height - 5, True)
        self.corner_handle.set_position(self.x + self.width - 5, self.y + self.height - 5, True)

    def draw(self, cr):
        cr.translate(self.x, self.y)
        cr.set_line_width(1)
        cr.set_source_rgb(0.2, 0.2, 0.3)
        cr.rectangle(0, 0, int(self.width) - 0.5, int(self.height) - 0.5)
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

        ResizableRectangle(self.canvas, 50, 150, 80, 50)
        ResizableRectangle(self.canvas, 100, 250, 180, 150)

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()

