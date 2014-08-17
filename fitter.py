"""
Fitting module: fit tracks to hits contained within a detector with the help
of the Kalman Filter.
"""
from matrix import Matrix
from detector import Detector
from filter import TwoWayLKFilter
from copy import copy


class FitManager(object):
    """A class that manages the fitting process."""

    def __init__(self, det_obj, filt_obj):
        assert isinstance(det_obj, Detector)
        assert isinstance(filt_obj, TwoWayLKFilter)
        self.detect = det_obj
        self.filt = filt_obj
        filt_obj.reverse()
        self.fitters = []

    def _new_filters(self, layer):
        """Spawn new filters for hits that could not be assigned to existing
        filters."""
        for strip in layer.hit_strips:
            for i in xrange(strip.hits):
                    # Create a copy of the filter (all the same matrices)
                    kfilter = copy(self.filt)
                    x, y = strip.pos()
                    # initialize with first hit
                    state = Matrix([[y, y / x]]).T
                    cov = Matrix([[10.0, 0.0],
                                  [0.0, 10.0]])
                    # thanks to this the becomes decoupled from the others
                    kfilter.state = state, cov
                    self.fitters.append(kfilter)
                    kfilter.step()
                    layer.clear_hits()

    def fit(self):
        """Perform a fit of the hits in the detector using the supplied
        Kalman Filter."""
        layers = self.detect.get_layers(reverse=True)
        # special procedure for first layer
        layer = next(layers)
        self._new_filters(layer)

        # Procedure for the remaining layers
        for layer in layers:
            for fitter in self.fitters:
                state, P = fitter.state
                y = state[0][0]
                y_err = P[0][0]
                # find the strip that minimizes the distance to the predicted
                # position y position
                strip = min(layer.hit_strips, key=
                            lambda strip: abs(y - strip.pos()[1]))
                measured_y = strip.pos()[1]
                # allow for 3 sigma distance (remember y_err is variance)
                if (measured_y - y) ** 2 > 9 * y_err:
                    # step ignoring the measurement
                    fitter.step()
                    continue
                else:
                    measurement = Matrix([[measured_y]])
                    fitter.step(measurement)
                    # decrement the amount of hits in strip or remove strip
                    # from hit_strips
                    if strip.hits == 1:
                        layer.hit_strips.remove(strip)
                    else:
                        strip.hits -= 1
            # now time to spawn new filters for measurements that have not been
            # assigned
            self._new_filters(layer)

        return self.fitters

