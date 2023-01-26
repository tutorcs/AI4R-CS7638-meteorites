https://tutorcs.com
WeChat: cstutorcs
QQ: 749389476
Email: tutorcs@163.com
######################################################################
# This file copyright the Georgia Institute of Technology
#
# Permission is given to students to use or modify this file (only)
# to work on their assignments.
#
# You may NOT publish this file or make it available to others not in
# the course.
#
######################################################################

# Optional: You may use deepcopy to help prevent aliasing
# from copy import deepcopy

# You may use either the numpy library or Sebastian Thrun's matrix library for
# your matrix math in this project; uncomment the import statement below for
# the library you wish to use, and ensure that the library you are not using is
# commented out.
# import numpy as np
# from matrix import matrix

# If you see different scores locally and on Gradescope this may be an
# indication that you are uploading a different file than the one you are
# executing locally. If this local ID doesn't match the ID on Gradescope then
# you uploaded a different file.
OUTPUT_UNIQUE_FILE_ID = False
if OUTPUT_UNIQUE_FILE_ID:
    import hashlib, pathlib
    file_hash = hashlib.md5(pathlib.Path(__file__).read_bytes()).hexdigest()
    print(f'Unique file ID: {file_hash}')


class Turret(object):
    """The laser used to defend against invading Meteorites."""

    def __init__(self, init_pos, max_angle_change,
                 dt):
        """Initialize the Turret."""
        self.x_pos = init_pos['x']
        self.y_pos = init_pos['y']
        self.max_angle_change = max_angle_change
        self.dt = dt

    def predict_from_observations(self, meteorite_observations):
        """Observe meteorite locations and predict their positions at time t+1.

        Parameters
        ----------
        self = a reference to the current object, the Turret
        meteorite_observations = a list of noisy observations of
            meteorite locations, taken at time t

        Returns
        -------
        A tuple or list of tuples containing (i, x, y), where i, x, and y are:
        i = the meteorite's ID
        x = the estimated x-coordinate of meteorite i's position for time t+1
        y = the estimated y-coordinate of meteorite i's position for time t+1

        Return format hint:
        For a tuple of tuples, this would look something like
        ((1, 0.4, 0.381), (2, 0.77, 0.457), ...)
        For a list of tuples, this would look something like
        [(1, 0.4, 0.381), (2, 0.77, 0.457), ...]

        Notes
        -----
        Each observation in meteorite_observations is a tuple
        (i, x, y), where i is the unique ID for an meteorite, and x, y are the
        x, y locations (with noise) of the current observation of that
        meteorite at this timestep. Only meteorites that are currently
        'in-bounds' will appear in this list, so be sure to use the meteorite
        ID, and not the position/index within the list to identify specific
        meteorites.
        The list/tuple of tuples you return may change in size as meteorites
        move in and out of bounds.
        """
        # TODO: Update the Turret's estimate of where the meteorites are
        # located at the current timestep and return the updated estimates

        return ((1, 0.5, 0.5),)

    def get_laser_action(self, current_aim_rad):
        """Return the laser's action; it can change its aim angle or fire.

        Parameters
        ----------
        self = a reference to the current object, the Turret
        current_aim_rad = the laser turret's current aim angle, in radians,
            provided by the simulation.


        Returns
        -------
        Float (desired change in laser aim angle, in radians), OR
            String 'fire' to fire the laser

        Notes
        -----
        The laser can aim in the range [0.0, pi].

        The maximum amount the laser's aim angle can change in a given timestep
        is self.max_angle_change radians. Larger change angles will be
        clamped to self.max_angle_change, but will keep the same sign as the
        returned desired angle change (e.g. an angle change of -3.0 rad would
        be clamped to -self.max_angle_change).

        If the laser is aimed at 0.0 rad, it will point horizontally to the
        right; if it is aimed at pi rad, it will point to the left.

        If the value returned from this function is the string 'fire' instead
        of a numerical angle change value, the laser will fire instead of
        moving.
        """
        # TODO: Update the change in the laser aim angle, in radians, based
        # on where the meteorites are currently, OR return 'fire' to fire the
        # laser at a meteorite

        return 0.0  # or 'fire'


def who_am_i():
    # Please specify your GT login ID in the whoami variable (ex: jsmith322).
    whoami = ''
    return whoami
