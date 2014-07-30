""" A module implementing various tracks. """
# pylint: disable=R0903,C0103


class Track(object):

    """ A track interface. """

    def __init__(self):
        pass

    def get_yintercept(self, x):
        """ Return y intercept of track with detector. """
        pass


class LineTrack(Track):

    """ A straight line track with the equation :math:`y = a x + b`. """

    def __init__(self, a, b):
        super(LineTrack, self).__init__()
        self.a = a
        self.b = b

    def get_yintercept(self, x):
        return self.a * x + self.b
