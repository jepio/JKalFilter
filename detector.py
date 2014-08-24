""" Module implementing the detector and detector response system. """
# pylint: disable=C0103,R0913,W0613,W0201,W0141
import math
from track import Track
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
            raise RuntimeError("Wrong x of layer")
        # Needs to be this way for the rare case where y == self.top, because
        # I'm going to use floor (without the equals sign it would attempt to
        # hit the non-existant detector above).
        if y >= self.top or y < self.bottom:
            return
        # Increment hits in parent(LayeredDetector) and self
        self.parent.hit(None, None)
        super(Layer, self).hit(x, y)
        # Increment the proper strip and add strip to hit_strips list
        num_strip = int(math.floor((y - self.bottom) / self.strip_height))
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
        try:
            x_step = float(length) / (num_layers - 1)
        except ZeroDivisionError:
            # If number of layers is 1 it means only one layer is going to be
            # created
            x_step = 0
        self.layers = [None for _ in xrange(num_layers)]

        for i in xrange(num_layers):
            new_x = x + i * x_step
            self.layers[i] = Layer(new_x, y, height, num_strips, parent=self)

    def get_layers(self, reverse=False):
        """Return the layers in the detector."""
        # layers are sorted by x position
        layers = sorted(self.layers, key=lambda i: i.pos()[0])
        if reverse:
            layers = reversed(layers)
        for layer in layers:
            yield layer

    def draw(self):
        """ Draw the detector with points in each strip center. """
        x = []
        y = []
        hits_x = []
        hits_y = []
        hit_mult = []
        for layer in self.get_layers():
            for strip in layer.strips:
                temp_x, temp_y = strip.pos()
                x.append(temp_x)
                y.append(temp_y)
            for strip in layer.hit_strips:
                temp_x, temp_y = strip.pos()
                mulitplicity = strip.hits
                hits_x.append(temp_x)
                hits_y.append(temp_y)
                hit_mult.append(mulitplicity)

        #print "Detector positions:"
        #print '\n'.join(map(str, zip(x, y)))
        print "\nHit positions:\n======================="
        print '\n'.join(map(str, zip(hits_x, hits_y, hit_mult)))
        plt.scatter(x, y, color='b')
        plt.scatter(hits_x, hits_y, color='r')
        plt.title("Layered Detector")
        plt.show()

    def clear_hits(self):
        for layer in self.get_layers():
            layer.clear_hits()
        self.hits = 0

    def propagate_track(self, track):
        """ Propagate track through detector, leaving hits in strips. """
        assert isinstance(track, Track)
        # Sort layers according to x position (just in case)
        for layer in self.get_layers():
            x, _ = layer.pos()
            y = track.get_yintercept(x)
            layer.hit(x, y)
