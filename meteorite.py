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
import numpy as np
import math
import random


def distance_formula(pt_0, pt_1):
    """Compute the 2D distance between point 0 and point 1."""
    return np.sqrt((pt_1[0] - pt_0[0])**2 + (pt_1[1] - pt_0[1])**2)


def right_angle_dist_to_line(line_pt_0, line_pt_1, point):
    """Compute the shortest distance between point and any point along a line.

    The line is defined by the endpoints, line_pt_0 and line_pt_1.
    For our application in this file, line_pt_0 is the turret location.
    Reference:
    https://mathworld.wolfram.com/Point-LineDistance2-Dimensional.html
    """
    vector = np.array([line_pt_1[1] - line_pt_0[1],
                       -(line_pt_1[0] - line_pt_0[0])])
    vector_r_to_v = np.array([line_pt_0[0] - point[0],
                              line_pt_0[1] - point[1]])

    dist = np.dot(vector, vector_r_to_v)
    return dist


class Meteorite(object):
    """An meteorite trying to invade Earth."""

    def __init__(self, meteorite_params, accel_factor,
                 laser_effectiveness_distance):
        """Initialize the Meteorite and its motion coefficients."""
        self.c_pos_x = meteorite_params['c_pos_x']
        self.c_vel_x = meteorite_params['c_vel_x']
        self.c_accel = meteorite_params['c_accel']
        self.c_pos_y = meteorite_params['c_pos_y']
        self.c_vel_y = meteorite_params['c_vel_y']
        self.t_start = meteorite_params['t_start']
        self.id = meteorite_params['id']
        self.accel_factor = accel_factor
        self.laser_effectiveness_distance = laser_effectiveness_distance

    def xy_pos(self, t):
        """Return the x-y position of this Meteorite."""
        t_shifted = t - self.t_start

        x_pos = ((0.5 * self.c_accel * self.accel_factor * t_shifted * t_shifted)
                 + (self.c_vel_x * t_shifted)
                 + self.c_pos_x)

        y_pos = ((0.5 * self.c_accel * t_shifted * t_shifted)
                 + (self.c_vel_y * t_shifted)
                 + self.c_pos_y)
        return (x_pos, y_pos)

    @property
    def params(self):
        """Return parameters of this Meteorite."""
        return {'c_pos_x':     self.c_pos_x,
                'c_vel_x':     self.c_vel_x,
                'c_accel':     self.c_accel,
                'c_pos_y':     self.c_pos_y,
                'c_vel_y':     self.c_vel_y,
                't_start': self.t_start,
                'id': self.id
                }

    def deactivate(self):
        """Deactivate this meteorite."""
        self.id = -1


class MeteorShower(object):
    """A collection of Meteorites."""

    def __init__(self, thearena, seed, p_hit, laser_effectiveness_distance,
                 meteorites, turret, margin):
        """Initialize the collection of Meteorites."""
        self.meteorites = meteorites
        self.arenacontains = thearena.contains
        self.x_bounds = thearena.bounds['x']
        self.y_bounds = thearena.bounds['y']
        self.turret = turret
        self.turret_pos = np.array([turret.x_pos, turret.y_pos]).copy()
        self.margin = margin
        self.laser_effectiveness_distance = laser_effectiveness_distance
        self.random_state = random.Random(seed)
        self.p_hit = p_hit

    def meteorite_locations(self, time):
        """Return the meteorites' locations.

        This returns a list of tuples, each of which contains a specific
        meteorite's index, x-position, and y-position.
        """
        locs = []
        for i, meteorite in enumerate(self.meteorites):
            if meteorite.t_start <= time:
                xyloc = meteorite.xy_pos(time)
                if self.arenacontains((xyloc[0], xyloc[1])):
                    locs.append((meteorite.id, xyloc[0], xyloc[1]))

        return locs

    def laser_or_ground_hit(self, time, laser_heading_rad,
                            laser_shots_remaining, laser_on):
        """Delete meteorites that hit the ground or were hit by the laser."""
        health_losses = [0]
        laser_line = [self.turret_pos[0] + math.cos(laser_heading_rad),
                      self.turret_pos[1] + math.sin(laser_heading_rad)]
        for meteorite in self.meteorites:
            if meteorite.id < 0:
                continue
            # check for ground hits
            if meteorite.xy_pos(time)[1] < self.turret.y_pos:
                meteorite.deactivate()
                if self.x_bounds[0] < meteorite.xy_pos(time)[0] < self.x_bounds[1]:
                    health_losses.append(1)
            if laser_on:
                if self.check_for_laser_hit(time, laser_line,
                                            laser_heading_rad,
                                            laser_shots_remaining,
                                            meteorite.xy_pos(time)):
                    meteorite.deactivate()
        return np.sum(health_losses)

    def check_for_laser_hit(self, time, laser_line, laser_hdg_rad,
                            laser_shots_remaining, meteorite_pos):
        """Return True if meteorite hit by laser, False otherwise."""
        if laser_shots_remaining <= 0:
            return False
        if distance_formula([self.turret_pos[0], self.turret_pos[1]],
                            meteorite_pos) > self.laser_effectiveness_distance:
            # meteorite is too far away from laser turret to be hit
            return False
        same_side = False

        if laser_hdg_rad > 0.5*math.pi and laser_hdg_rad <= math.pi:
            # laser turret aimed in the left half of the arena
            if (self.turret_pos[0] - meteorite_pos[0]) > 0:
                same_side = True
        elif laser_hdg_rad < 0.5*math.pi and laser_hdg_rad >= 0.0:
            # laser turret aimed in the right half of the arena
            if (self.turret_pos[0] - meteorite_pos[0]) < 0:
                same_side = True
        elif laser_hdg_rad == 0.5*math.pi:
            # laser points straight up, so check whether meteorite is within a
            # small distance of the laser pointing straight up
            if abs((self.turret_pos[0] - meteorite_pos[0]) < self.margin):
                same_side = True

        if same_side and abs(right_angle_dist_to_line((self.turret_pos[0],
                                                       self.turret_pos[1]),
                             laser_line, meteorite_pos)) < self.margin:
            if not meteorite_pos[0] > self.turret_pos[0] > laser_line[0] or \
                    not meteorite_pos[0] < self.turret_pos[0] < laser_line[0]:
                if self.random_state.random() <= self.p_hit:
                    return True
        return False

    def check_for_ground_hit(self, time, ground_y, meteorite):
        """Return -1 if the meteorite hits the ground and will deduct health.

        If the meteorite hits the ground outside of the x-coordinate limits
        of the arena, the health loss is not counted.
        The meteorite is ignored if its ID is < 0 (already deactivated).
        """
        if meteorite.id < 0:
            return 0
        if meteorite.xy_pos(time)[1] < self.y_bounds[0]:
            meteorite.deactivate()
            if self.x_bounds[0] < meteorite.xy_pos(time)[0] < self.x_bounds[1]:
                return -1
