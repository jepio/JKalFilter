""" Test of fitting. """
# pylint: disable=C0103
from matrix import Matrix
from detector import LayeredDetector
from track import gen_straight_tracks
from matplotlib import pyplot as plt
from fitter import FitManager
from kfilter import TwoWayLKFilter
plt.ion()


def main():
    # length
    Lx = 8
    Ly = 1.0
    # number of layers/strips
    Nx = 15
    Ny = 25
    # y error (uniform)
    y_err = Ly / (Ny * 12 ** 0.5)
    dx = float(Lx) / (Nx - 1)
    detector = LayeredDetector(1, 0, Ly, Lx, Nx, Ny)
    tracks = gen_straight_tracks(5)
    x_coords = [0.1 * i for i in xrange(100)]
    detector.propagate_tracks(tracks)
    for track in tracks:
        y = [track.get_yintercept(x) for x in x_coords]
        #plt.plot(x_coords, y)
    plt.xlim(0, 10)
    plt.ylim(-1.5, 1.5)
    #plt.gca().set_aspect('equal')
    detector.draw(True)

    # measurement matrix
    H = Matrix([[1.0, 0.0]])
    # transition matrix
    A = Matrix([[1.0,  dx],
                [0.0, 1.0]])
    # process error
    Q = Matrix([[0.00005, 0.0],
                [0.0, 0.00005]])
    R = Matrix([[1*y_err]])
    # dummy measurement - filter needs to know the shape of measurements
    x = Matrix([[0, 0]]).T
    kal_filter = TwoWayLKFilter(A, H, x, None, Q, R)
    fitter = FitManager(detector, kal_filter)
    fitters = fitter.fit()

    print "\nFitted hits:\n======================="
    for filt in fitters:
        print filt.measurements_list

    track_coordinates = fitter.propagate_tracks()
    for track in track_coordinates:
        x, y = zip(*track)
        plt.plot(x,y)

if __name__ == "__main__":
    main()
    raw_input()
