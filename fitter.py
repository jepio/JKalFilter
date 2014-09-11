"""
Fitting module: fit tracks to hits contained within a detector with the help
of Kalman Filters.
"""
from matrix import Matrix
from detector import Detector
from kfilter import TwoWayLKFilter
from copy import copy


class FitManager(object):
    """A class that manages the fitting process. It takes a detector object
    containing hits and a Kalman filter object with matrices describing the
    model with which to perfom the fit. Due to the method used for the fit,
    which involves starting at the back of the detector (far from the vertex),
    iterating backwards and then forwards again, the supplied Kalman filter
    object must subclass the :py:class:`kfilter.TwoWayLKFilter` so that iteration
    can be reversed.

    :param Detector det_obj: detector containing hits to which tracks are to be
     fitted
    :param TwoWayLKFilter filt_obj: a Kalman filter object using which the tracks
     will be fitted.
    """

    def __init__(self, det_obj, filt_obj):
        assert isinstance(det_obj, Detector)
        assert isinstance(filt_obj, TwoWayLKFilter)
        self.detector = det_obj
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
                # thanks to this the filter becomes decoupled from the
                # original
                kfilter.state = state, cov
                self.fitters.append(kfilter)
                kfilter.step(add=True)
        layer.clear_hits()

    def fit(self):
        """Perform a fit of the hits in the detector using the supplied
        Kalman filter. After tracks have been fitted to the hits, this method
        returns a list of Kalman filter objects, each of which contains the
        hits that have been assigned to it. The filters are in the state
        corresponding to the *x* position one layer distance past the first layer.

        Before the filters are returned, the ones with less than 3 measurements
        assigned to them are removed as unreliable fits. The quickest way to use
        the fitted tracks is to get their :py:attr:`measurements_list`::

            >>> ftr = FitManager(det_obj, filtr_obj)
            >>> kfilters = ftr.fit()
            >>> for track_y_hits in kfilters.measurements_list:
            ...     # do something with y hits of each track

        :returns: one Kalman filter object for each track that has been assigned
         to the hits in the detector
        :rtype: *list(TwoWayLKFilter)*
        """
        layers = self.detector.get_layers(reverse=True)
        # special procedure for first layer
        layer = next(layers)
        self._new_filters(layer)

        # Procedure for the remaining layers
        for layer in layers:
            for fitter in self.fitters:
                # TODO: investigate hungarian algorithm for assigning hits to
                # filters
                state, cov_matrix = fitter.state
                predicted_y = state[0][0]
                y_err = cov_matrix[0][0]
                # find the strip that minimizes the distance to the predicted
                # y position
                if layer.hit_strips:  # if it's not empty
                    strip = min(layer.hit_strips, key=
                                lambda strip: abs(predicted_y - strip.pos()[1]))
                    measured_y = strip.pos()[1]
                else:
                    measured_y = None
                # allow for 3 sigma distance (remember y_err is variance)
                if ((measured_y is None) or
                        ((measured_y - predicted_y) ** 2 > 9 * y_err)):
                    # step ignoring the measurement
                    fitter.step(add=True)
                    continue
                else:
                    measurement = Matrix([[measured_y]])
                    fitter.step(measurement, add=True)
                    # decrement the amount of hits in strip or remove strip
                    # from hit_strips
                    if strip.hits == 1:
                        layer.hit_strips.remove(strip)
                    else:
                        strip.hits -= 1
            # now time to spawn new filters for measurements that have not been
            # assigned
            self._new_filters(layer)

        # Selection based on amount of measurements
        self.fitters = [x for x in self.fitters if len(x.measurements) > 2]
        return self.fitters

    def propagate_tracks(self):
        """Propagate all fitted tracks back towards the back of the detector.
        This function is meant to be used directly after :py:meth:`fit` to give
        more usable data back to the user. It returns a list of tracks, where each
        track is represented by a list of *x* and *y* pairs. Each of these pairs
        corresponds to the filtered coordinates of a hit assigned to the track.
        A quick way to get *x* and *y* lists for each track is the following::

            >>> ftr = FitManager(det_obj, filt_obj)
            >>> ftr.fit()
            >>> tracks = ftr.propagate_tracks()
            >>> for track in tracks:
            ...     x, y = zip(*track)
            ...     # work with coordinates, e.g. plot(x,y)
            ...

        :returns: list of filtered track coordinates
        :rtype: *list(list(tuple))*
        """
        x_step = self.detector.x_step
        start_x = self.detector.pos()[0]  # x position of left-most layer
        result = []
        for fitter in self.fitters:
            estimates = []
            fitter.reverse()
            current_x = start_x - x_step
            # state vector, then position in state vector
            current_y = fitter.state[0][0][0]
            # initial coordinates
            estimates.append((current_x, current_y))

            # One step needs to be performed since filter is set up to first
            # update then predict.
            state, _ = fitter.step(None)
            current_y = state[0][0]
            current_x += x_step
            estimates.append((current_x, current_y))

            for state, _ in fitter:
                current_y = state[0][0]  # col. vect: contains y and y'
                current_x += x_step
                estimates.append((current_x, current_y))

            result.append(estimates)
        return result
