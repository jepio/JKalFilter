""" Test of tracking and detector response. """
# pylint: disable=C0103
from detector import LayeredDetector
from track import LineTrack
from matplotlib import pyplot as plt

def main():
    """
    Test if construction of detector works and propagate tracks through
    detector.
    """
    A = LayeredDetector(1, 0, 0.5, 8, 80, 100)
    T = LineTrack(-0.05, 0.29995)
    T2 = LineTrack(0.05, -0.3)
    A.propagate_track(T)
    A.propagate_track(T2)
    x = [0.1 * i for i in xrange(90)]
    y = [T.get_yintercept(i) for i in x]
    y2 = [T2.get_yintercept(i) for i in x]
    plt.plot(x, y2)
    plt.plot(x, y)
    A.draw()


if __name__ == "__main__":
    main()
