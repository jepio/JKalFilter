""" A module implementing various tracks. """
# pylint: disable=R0903,C0103


def unimplemented(function):
    def decorated_func(*ar, **kw):
        raise AttributeError(
            "Unimplemented abstract method " + function.__name__)
    return decorated_func


class Track(object):

    """ A track interface. """

    @unimplemented
    def __init__(self):
        pass

    @unimplemented
    def get_yintercept(self, x):
        """ Return y intercept of track with detector. """
        pass


class LineTrack(Track):

    """ A straight line track with the equation :math:`y = a x + b`. """

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def get_yintercept(self, x):
        return self.a * x + self.b
