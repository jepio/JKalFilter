""" A module implementing various tracks. """
# pylint: disable=R0903,C0103
import random
import math


class Track(object):

    """ A track interface. """

    def __init__(self):
        raise NotImplementedError

    def get_yintercept(self, x):
        """ Return y intercept of track with detector. """
        raise NotImplementedError


class LineTrack(Track):

    """ A straight line track with the equation :math:`y = a x + b`. """

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get_yintercept(self, x):
        return self.a * x + self.b

class MagneticTrack(LineTrack):

    """A track moving in a magnetic field."""

    def __init__(self, a, b, B):
        """Create a straight line track that propagates in a magnetic field of
        strength `B` in z direction."""
        super(MagneticTrack, self).__init__(a, b)
        self.B = B


    def get_yintercept(self, x):
        """Return y intercept of track with detector at x.
        This takes into account the magnetic field."""
        alpha = math.atan(self.a)
        vx0, vy0 = (self.a * math.cos(alpha), self.a * math.sin(alpha))
        yy = (abs((self.a/self.B)**2 - (x - vy0/self.B)**2)**0.5
              + (self.b-vx0/self.B))
        return yy

def gen_straight_tracks(N=10):
    """Generate tracks that will be propagated through detector"""
    tracks = [None] * N
    random.seed()
    random_nums = ((random.random(), random.random()) for i in xrange(N))
    for i in xrange(N):
        a, b = next(random_nums)
        # generate b of track from uniform
        b = 0.2 * (b - 0.5)
        # generate a of track so that the angles are uniform from 15 degrees to
        # -15 degrees.
        a = math.tan(math.pi / 6 * (a - 0.5))
        tracks[i] = LineTrack(a, b)
    return tracks
