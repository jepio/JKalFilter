""" A module for testing the functioning of the kfilter module. """
from kfilter import LKFilter
from matrix import Matrix
import random
import sys
# pylint: disable=C0103,W0141,R0914

def pretty_output(*args):
    output = [' '.join(map("{:.5f}".format, entry)) for entry in
              zip(*args)]
    string_output = '\n'.join(output)
    print string_output

def test(N=10):
    """ Test a simple KF. """
    dt = 1.0
    x0 = 0.0
    # Linear system
    init_state = Matrix([[x0, 0.0]]).T
    init_cov = Matrix([[100.0, 0.],
                       [0., 100.0]])
    H = Matrix([[1.0, 0.0]])
    A = Matrix([[1.0, dt],
                [0.0, 1.]])
    Q = Matrix([[0.0001, 0.0],
                [0.0, 0.0001]])
    R = Matrix([[5.0]])

    rand = random.gauss
    meas_list = [i + rand(0, 2) for i in xrange(N)]
    measurements = [Matrix([[meas]]) for meas in meas_list]

    filt = LKFilter(A, H, init_state, init_cov, Q, R)
    results = [x0]

    filt.add_meas(measurements)
    for new, _ in filt:
        results.append(new[0][0])

    pretty_output(meas_list, results)

def test_square(N=10):
    dt = 0.2
    x0 = 0.0
    x = Matrix([[x0, 0.0, 0.0]]).T
    P = Matrix([[100.0, 0., 0.],
                [0., 100.0, 0.],
                [0., 0., 100.0]])
    H = Matrix([[1.0, 0.0, 0.0]])
    A = Matrix([[1.0,  dt, 0.5*dt**2],
                [0.0, 1.0,        dt],
                [0.0, 0.0,       1.0]])
    Q = Matrix([[0.0001, 0.0, 0.0],
                [0.0, 0.0001, 0.0],
                [0.0, 0.0, 0.0001]])
    R = Matrix([[1.0]])

    rand = random.gauss
    meas_list = [2+(i*dt)**2 + rand(0, 1) for i in xrange(N)]
    measurements = [Matrix([[meas]]) for meas in meas_list]
    filt = LKFilter(A, H, x, P, Q, R)
    results = [x0]
    v = [0.0]
    a = [0.0]
    filt.add_meas(measurements)
    for new, _ in filt:
        results.append(new[0][0])
        v.append(new[1][0])
        a.append(new[2][0])

    pretty_output(meas_list, results, v, a)



if __name__ == "__main__":
    funcs = {'1':test, '2':test_square}
    if len(sys.argv) == 3:
        funcs[sys.argv[1]](int(sys.argv[2]))
    else:
        print("USAGE: test_filter function_num num_iterations")
        print("Functions: " + str(funcs))
