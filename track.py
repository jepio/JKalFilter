"""A module implementing various physical tracks that represent objects being
tracked. This module is meant to gather all possible tracks. Two dimensional
tracks should extend the :py:class:`.Track` abstract base class. Currently the
:py:class:`LineTrack` class has been implemented."""
# pylint: disable=R0903,C0103
import random
import math


class Track(object):

    """A two dimension track interface interface. The interface enforces that
    subclasses implement a constructor and a :py:meth:`get_yintercept` function.
    """

    def __init__(self):
        raise NotImplementedError

    def get_yintercept(self, x):
        """Return **y** intercept of track with detector.

        :param x: coordinate at which to calculate the interception point.
        :type x: float
        :return: **y** value of track for a given **x**
        :rtype: *float*
        """
        raise NotImplementedError


class LineTrack(Track):

    """ A straight line track with the equation :math:`y = a x + b`.

    :param a: slope of track
    :type a: float
    :param b: **y** intercept at 0
    :type b: float"""

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get_yintercept(self, x):
        return self.a * x + self.b


class MagneticTrack(LineTrack):
    """A track moving in a magnetic field. Experimental and untested."""

    def __init__(self, a, b, B):
        """Create a straight line track that propagates in a magnetic field of
        strength `B` in z direction."""
        super(MagneticTrack, self).__init__(a, b)
        self.B = B


    def get_yintercept(self, x):
        """Return y intercept of track with detector at x, taking into account
        the curvature caused by the magnetic field."""
        alpha = math.atan(self.a)

        vx0, vy0 = (self.a * math.cos(alpha), self.a * math.sin(alpha))
        yy = (abs((self.a/self.B)**2 - (x - vy0/self.B)**2)**0.5
              + (self.b-vx0/self.B))
        return yy

def gen_straight_tracks(N=10):
    """Helper function to generate multiple :py:class:`LineTrack` objects that
    can then be used, e.g. for propagating in a detector. The tracks are
    generated using random numbers to generate the track parameters **a** and
    **b**. Currently the parameter ranges are not adjustable and are the following:

    * **a** from -0.268 to 0.268 (corresponds to an angle of -15 to 15 degrees)
    * **b** from -0.1 to 0.1

    :param int N: amount of tracks to return
    :return: generated tracks
    :rtype: *list(LineTrack)*
    """
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
