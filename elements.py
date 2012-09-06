from math import sqrt
from scipy.integrate import quad

def vector_length(v):
    return sqrt(v[0]*v[0] + v[1]*v[1])

class Element(object):
    def _points(self, count):
        prev = self.start
        yield prev
        for tr in xrange(1, count + 1):
            t = float(tr) / count
            p = self.p(t)
            yield p
            prev = p

    def points(self, stitch_length, stitch_distance):
        if self.thickness < stitch_length:
            stitches = int(round(self.length() / stitch_length))
            for p in self._points(stitches):
                yield p
        else:
            stitches = int(round(self.length() / stitch_distance))
            t = max(self.thickness, stitch_length) / 2

            prev = None
            for p in self._points(stitches):
                if prev:
                    n = (p[1] - prev[1], prev[0] - p[0])
                    l = vector_length(n)
                    n = (n[0] * t / l, n[1] * t / l)
                    yield (p[0] + n[0], p[1] + n[1])
                    yield (p[0] - n[0], p[1] - n[1])
                else:
                    yield p
                prev = p

    def revert(self):
        pass

class Line(Element):
    def __init__(self, start, finish, thickness=None):
        self.start = start
        self.finish = finish
        self.thickness = thickness

    def p(self, t):
        def b(p0, p1, t):
            return (1-t)*p0 + t*p1
        return (
            b(self.start[0], self.finish[0], t),
            b(self.start[1], self.finish[1], t),
        )

    def length(self):
        dx = self.start[0] - self.finish[0]
        dy = self.start[1] - self.finish[1]
        return sqrt(dx*dx + dy*dy)

    def draw(self, w):
        w.create_line(self.start[0], self.start[1], self.finish[0], self.finish[1], width=self.thickness)

class CubicBezier(Element):
    def __init__(self, start, hp1, hp2, finish, thickness=None):
        self.start = start
        self.hp1 = hp1
        self.hp2 = hp2
        self.finish = finish
        self.thickness = thickness

    def revert(self):
        self.start, self.hp1, self.hp2, self.finish = self.finish, self.hp2, self.hp1, self.start

    def p(self, t):
        def b(p0, p1, p2, p3, t):
            return (1-t)*(1-t)*(1-t)*p0 +3*t*(1-t)*(1-t)*p1 + 3*t*t*(1-t)*p2 + t*t*t*p3
        return (
            b(self.start[0], self.hp1[0], self.hp2[0], self.finish[0], t),
            b(self.start[1], self.hp1[1], self.hp2[1], self.finish[1], t),
        )

    def length(self):
        def diff_b(p0, p1, p2, p3, t):
            return 3*t*t*(p3 - p2) + 6*(1-t)*t*(p2 - p1) + 3*(1-t)*(1-t)*(p1 - p0)

        def i(t):
            dx = diff_b(self.start[0], self.hp1[0], self.hp2[0], self.finish[0], t)
            dy = diff_b(self.start[1], self.hp1[1], self.hp2[1], self.finish[1], t)
            return sqrt(dx*dx + dy*dy)

        return quad(i, 0, 1)[0]

    def draw(self, w):
        prev = self.start
        for tr in xrange(1, 201):
            t = tr / 200.0
            p = self.p(t)
            w.create_line(prev[0], prev[1], p[0], p[1], width=self.thickness)
            prev = p

