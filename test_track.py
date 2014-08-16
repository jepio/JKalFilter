""" Test of tracking and detector response. """
# pylint: disable=C0103
from detector import LayeredDetector
from track import gen_straight_tracks
from matplotlib import pyplot as plt


def main():
    """
    Test if construction of detector works and propagate tracks through
    detector.
    """
    A = LayeredDetector(1, 0, 0.5, 8, 10, 25)
    tracks = gen_straight_tracks(20)
    x_coords = [0.1 * i for i in xrange(100)]
    for i, track in enumerate(tracks):
        A.propagate_track(track)
        y = [track.get_yintercept(x) for x in x_coords]
        plt.plot(x_coords, y)
    plt.xlim(0, 10)
    plt.ylim(-0.5, 0.5)
    A.draw()



if __name__ == "__main__":
    main()
