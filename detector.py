""" Module implementing the detector and detector response system. """
# pylint: disable=C0103,R0913,W0613,W0201
import math
from matplotlib import pyplot as plt


class Detector(object):

    """ Abstract detector interface, to be inherited by all detectors. """

    def __init__(self, x, y, x_err=0, y_err=0):
        types = [int, float]
        assert type(x) in types
        assert type(y) in types
        self.x = x
        self.y = y
        self.x_err = x_err
        self.y_err = y_err
        self.hits = 0

    def hit(self, x, y):
        """ Increment the amount of hits in this detector. """
        self.hits += 1

    def pos(self):
        """ Get the position of the detector. """
        return (self.x, self.y)

    def clear_hits(self):
        """ Clear hits from detector """
        self.hits = 0


class Strip(Detector):

    """ A strip detector, part of a layer. """

    def __init__(self, x, y, height, x_err=0, y_err=-1, parent=None):
        # Uniform distribution errors
        if y_err == -1:
            y_err = height / 12 ** 0.5
        super(Strip, self).__init__(x, y, x_err, y_err)
        self.height = height
        self.parent = parent


class Layer(Detector):

    """ A layer detector containing strips. """

    def __init__(self, x, y, height, num_strips, parent):
        super(Layer, self).__init__(x, y)

        bottom = y - height * 0.5
        self.bottom = bottom
        top = bottom + height
        self.top = top
        step = (top - bottom) / num_strips
        self.strip_height = step

        # Create strips for this layer
        self.strips = [None for _ in xrange(num_strips)]
        for i in xrange(num_strips):
            new_y = bottom + (i + 0.5) * step
            self.strips[i] = Strip(x, new_y, step, parent=self)

        self.hit_strips = []
        self.parent = parent

    def hit(self, x, y):
        """ Increment the hit amount in the correct strip. """
        if self.x != x:
            return
        if y > self.top or y < self.bottom:
            return
        super(Layer, self).hit(x, y)
        # Increment the proper strip and add strip to hit_strips list
        num_strip = math.floor((y - self.bottom) / self.strip_height)
        self.strips[num_strip].hit(x, y)
        if self.strips[num_strip] not in self.hit_strips:
            self.hit_strips.append(self.strips[num_strip])

    def clear_hits(self):
        for strip in self.hit_strips:
            strip.clear_hits()
        self.hit_strips = []
        self.hits = 0


class LayeredDetector(Detector):

    """ A layered detector, consisting of layers. """

    def __init__(self, x, y, height, length, num_layers, num_strips):
        super(LayeredDetector, self).__init__(x, y)
        x_step = float(length) / num_layers
        self.layers = [None for _ in xrange(num_layers)]

        for i in xrange(num_layers):
            new_x = x + i * x_step
            self.layers[i] = Layer(new_x, y, height, num_strips, parent=self)

    def draw(self):
        """ Draw the detector with points in each strip center. """
        x = []
        y = []
        hits_x = []
        hits_y = []
        for layer in self.layers:
            for strip in layer.strips:
                temp_x, temp_y = strip.pos()
                x.append(temp_x)
                y.append(temp_y)
            for strip in layer.hit_strips:
                temp_x, temp_y = strip.pos()
                hits_x.append(temp_x)
                hits_y.append(temp_y)
        print zip(x, y)
        print zip(hits_x, hits_y)
        plt.scatter(x, y, color='b')
        plt.scatter(hits_x, hits_y, color='r')
        plt.title("Layered Detector")
        plt.show()

    def clear_hits(self):
        for layer in self.layers:
            layer.clear_hits()
        self.hits = 0


def main():
    """ Test if construction of detector works. """
    A = LayeredDetector(1, 2, 0.5, 8, 8, 10)
    A.draw()

if __name__ == "__main__":
    main()
