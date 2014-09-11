""" Module implementing detectors and the detectors interaction with :py:mod:`track`. """
# pylint: disable=C0103,R0913,W0613,W0201,W0141
import math
from track import Track


class Detector(object):

    """Detector baseclass meant to be inherited by all detectors. Each
    detector should implement 3 functionalities:

    1. :py:meth:`clear_hits` to clear the hits stored in the detector
    2. :py:meth:`hit` to hit the detector at the correct location.
    3. :py:meth:`pos` to retries the position of the detector.

    This baseclass provides default implementations of these 3 methods, but
    they should be overridden for more complex detectors.

    :param float x: horizontal position of detector
    :param float y: vertical position of detector
    :param float x_err: measurement(hit) horizontal uncertainty
    :param float y_err: measurement(hit) vertical uncertainty
    :var int hits: amount of hits registered in this detector
    """

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
        """ Increment the amount of hits in this detector. The default
        implementation increments the count by one, not checking passed
        parameters"""
        self.hits += 1

    def pos(self):
        """ Get the position of the detector.

        :returns: position of the detector (**x**, **y**)
        :rtype: tuple(float)"""
        return (self.x, self.y)

    def clear_hits(self):
        """ Clear hits from detector """
        self.hits = 0


class Strip(Detector):

    """ A strip detector, designed to be part of a :py:class:`.Layer`. If
    *y_err* is ``None`` then the errors will be computed from uniform
    distribution errors. The default method implementations in :py:class:`Detector`
    are sufficient for this class.

    :param float x: horizontal position of detector
    :param float y: vertical position of detector
    :param float height: The vertical size of the detector
    :param float x_err: measurement(hit) horizontal uncertainty
    :param float y_err: measurement(hit) vertical uncertainty
    :param parent: a reference to the parent detector to which this strip
     belongs.
    """

    def __init__(self, x, y, height, x_err=0, y_err=None, parent=None):
        # Uniform distribution errors
        if y_err == None:
            y_err = height / 12 ** 0.5
        super(Strip, self).__init__(x, y, x_err, y_err)
        self.height = height
        self.parent = parent


class Layer(Detector):

    """ A layer detector containing many :py:class:`.Strip` detectors, meant to
    be part of a :py:class:`.LayeredDetector`. The :py:meth:`.clear_hits`
    implementation in this class removes hits from this detector and all
    detectors that belong to it. The tuple returned by :py:meth:`.pos` will hold
    the *x* position of the layer and the *y* position of the middle.

    Constructed strips will have *y* positions from ``y - height`` to
    ``y + height``.

    :param float x: horizontal position of detector
    :param float y: horizontal position of detector
    :param float height: the height of the whole layer
    :param int num_strips: the amount of strips of which the layer consists -
     they will be automatically constructed
    :param parent: a reference to the parent detector to which this strip
     belongs."""

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
        """ Increment the hit count in the correct strip. Will find the correct
        strip based on the passed *y* parameter. The *x* parameter should
        always be the same one as returned by ``self.pos()``.

        :param float x: **x** position of this detector
        :param float y: **y** position at which the detector was hit
        """
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

    """ A layered detector, consisting of many :py:class:`.Layer` detectors.
    Layers will be constructed based on the construction parameters. The
    :py:meth:`.pos` method will return the *y* position of the middle of all
    detectors and the *x* position of the leftmost layer. Layers will be
    constrcuted between ``x`` and ``x + length``. The *num_layers* parameter
    will be passed to the constructor of the :py:class:`Layer` objects.

    :param float x: horizontal position of detector
    :param float y: horizontal position of detector
    :param float height: the height of each layer
    :param float length: the length of the whole detector
    :param int num_layers: the number of layers that will be constructed -
     first one ``x``, last one at ``x + length``.
    :param int num_strips: the number of strips that will be constructed in
     **each** layer.
    """

    def __init__(self, x, y, height, length, num_layers, num_strips):
        super(LayeredDetector, self).__init__(x, y)
        try:
            x_step = float(length) / (num_layers - 1)
        except ZeroDivisionError:
            # If number of layers is 1 it means only one layer is going to be
            # created
            x_step = 0.0
        self.layers = [None for _ in xrange(num_layers)]
        for i in xrange(num_layers):
            new_x = x + i * x_step
            self.layers[i] = Layer(new_x, y, height, num_strips, parent=self)

    @property
    def x_step(self):
        """Return x distance between layers."""
        if len(self.layers) == 1:
            return 0
        # returns x position of a layer
        fun = lambda layer: layer.pos()[0]
        # distance between first two layers
        x_step = fun(self.layers[1]) - fun(self.layers[0])
        return x_step


    def get_layers(self, reverse=False):
        """Helper generator that yields the layers in the detector.

        :param bool reverse: toggle whether to yield in rising or falling *x*
         order """
        # layers are sorted by x position
        layers = sorted(self.layers, key=lambda i: i.pos()[0])
        if reverse:
            layers = reversed(layers)
        for layer in layers:
            yield layer

    def draw(self, rounding=False):
        """ Draw the detector with blue markers in the center of each strip of
        the detector and red markers at every registered hit. Pulls in
        `matplotlib <http://matplotlib.org>`_ as a dependency. Additionally
        prints the positions of all hits. If *rounding* is True rounds the
        printed floating point values to 5 decimal digits. """
        from matplotlib import pyplot as plt
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
                if rounding:
                    temp_x = round(temp_x,5)
                    temp_y = round(temp_y,5)
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
        """Propagate track through detector, leaving hits in strips. The
        passed track must extend the :py:class:`track.Track` baseclass. The
        propagated track will leave hits in the strips of this detector.

        :param track: track to propagate
        :type track: Track
        """
        assert isinstance(track, Track)
        # Sort layers according to x position (just in case)
        for layer in self.get_layers():
            x, _ = layer.pos()
            y = track.get_yintercept(x)
            layer.hit(x, y)

    def propagate_tracks(self, tracks):
        """Propagate all tracks from a list, leaving hits in the detector.

        :param tracks: tracks to be propagated through the detector
        :type tracks: list(Track)
        """
        assert isinstance(tracks, list)
        for track in tracks:
            self.propagate_track(track)
