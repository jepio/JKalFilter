""" Kalman Filter module """
# pylint: disable=C0103
from matrix import Matrix


class LKFilter(object):

    """
    A Linear Kalman Filter implementation.

    For more details on this implementation go to:
    http://greg.czerniak.info/guides/kalman1/
    """

    def __init__(self, _A, _H, _x, _P, _Q, _R):
        """
        Initialize the Kalman Filter matrices. This implementation skips the
        control input. Symbols used:

            A - state transition matrix - predict next state from current one
            H - measurement matrix, calculate measurement from the state
            x - initial estimate of the state
            P - initial estimate of the state covariance matrix
            Q - estimated process covariance
            R - estimated measurement covariance
            I - an identity matrix of size equal to dimension of the state
                vector
        """
        self.A = _A
        self.H = _H
        self.x = _x
        self.P = _P
        self.Q = _Q
        self.R = _R
        self.I = Matrix.identity(max(_x.size()))

    def get_state(self):
        """ Return current state vector and state covariance. """
        return (self.x, self.P)

    def update(self, measurement):
        """ Update current state using the measurement. """
        if measurement.size() != (self.H * self.x).size():
            raise Exception("Wrong vector shape")
        # Update
        y = measurement - self.H * self.x
        S = self.H * self.P * self.H.T + self.R
        K = self.P * self.H.T * S.I
        self.x = self.x + K * y
        self.P = (self.I - K * self.H) * self.P

    def predict(self):
        """ Predict the next state based on current state. """
        # Predict
        self.x = self.A * self.x
        self.P = self.A * self.P * self.A.T + self.Q

    def step(self, measurement):
        """
        Perform one iteration of the Kalman Filter:

            1. update state from measurement
            2. predict next state from current

        Depending on what is expected the order of these operations can also
        be inverted.
        """
        self.update(measurement)
        self.predict()
        return self.get_state()
