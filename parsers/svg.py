import re
from xml.sax import make_parser, handler
from elements import *

class SvgHandler(handler.ContentHandler):
    def __init__(self):
        self.paths = []

    def startElement(self, name, attrs):
        if name == 'path':
            self.paths.append((
                re.split('[,\s]+', attrs['d']),
                attrs['style']))

def read_file(source):
    parser = make_parser()
    handler = SvgHandler()
    parser.setContentHandler(handler)
    parser.parse(source)
    return handler.paths

class PathDataReader(object):
    def __init__(self, path_data):
        self.path_data = path_data
        self.position = 0

    def has_data(self):
        return self.position < len(self.path_data)

    def peek(self):
        if self.has_data():
            return self.path_data[self.position]
        else:
            return None

    def get(self):
        if not self.has_data():
            raise Exception('Aaa!!!')
        d = self.path_data[self.position]
        self.position += 1
        return d

    def get_point(self):
        if self.position + 2 > len(self.path_data):
            raise Exception('Aaa!!!')
        p = (
            float(self.path_data[self.position]),
            float(self.path_data[self.position + 1])
        )
        self.position += 2
        return p

    def get_relative_point(self, origin):
        p = self.get_point()
        return (p[0] + origin[0], p[1] + origin[1])

def interpret_path_data(path_data, style):
    def is_number(s):
        try:
            float(s)
            return True
        except (TypeError, ValueError):
            return False

    current_point = (0, 0)
    elements = []
    thickness = 1
    m = re.search('stroke-width:([-.0-9]+)', style)
    if m:
        thickness = float(m.group(1))

    reader = PathDataReader(path_data)
    while reader.has_data():
        command = reader.get()

        if command == 'M':
            current_point = reader.get_point()
            while is_number(reader.peek()):
                p = reader.get_point()
                elements.append(Line(current_point, p, thickness))
                current_point = p

        elif command == 'm':
            current_point = reader.get_relative_point(current_point)
            while is_number(reader.peek()):
                p = reader.get_relative_point(current_point)
                elements.append(Line(current_point, p, thickness))
                current_point = p

        elif command == 'C':
            f = False
            while is_number(reader.peek()):
                f = True
                p1 = reader.get_point()
                p2 = reader.get_point()
                p = reader.get_point()
                elements.append(CubicBezier(current_point, p1, p2, p, thickness))
                current_point = p
            if not f:
                raise Exception('Aaa!!!')

        elif command == 'c':
            f = False
            while is_number(reader.peek()):
                f = True
                p1 = reader.get_relative_point(current_point)
                p2 = reader.get_relative_point(current_point)
                p = reader.get_relative_point(current_point)
                elements.append(CubicBezier(current_point, p1, p2, p, thickness))
                current_point = p
            if not f:
                raise Exception('Aaa!!!')

        else:
            raise Exception('Unknown command "%s".' % command)

    return elements

def load_svg(filename):
    p = read_file(filename)
    elements = []
    for path_data, style in p:
        elements += interpret_path_data(path_data, style)
    return elements

