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

import argparse
import json
import os.path

import numpy as np
import math
import random

from meteorite import Meteorite, MeteorShower
from arena import FIELD_X_BOUNDS, FIELD_Y_BOUNDS
import arena
from turret import Turret


# these values are just fillers; we replace them with the actual args later
INITIAL_LASER_STATE = {"h": np.pi * 0.5,
                       "hp": 50,
                       "laser_shots_remaining": 50}

TURRET_INITIAL_POS = {'x': 0.0,
                      'y': -1.0}

P_HIT = 0.75

IN_BOUNDS = {"x_bounds": FIELD_X_BOUNDS,
             "y_bounds": FIELD_Y_BOUNDS}

TEENSY_COEFFICIENT = -1e-6
ACCEL_CORR_FACTOR_S = 1.0/3.0
MAX_MAGNITUDE_ACCEL = 1e-05
MIN_START_DIST_ABOVE_GROUND = 0.5
LASER_LENGTH = 1.1


class MeteorShowerGenerator(object):
    """Creates a group of Meteorites in random positions and initializes motion."""

    def __init__(self, seed):
        """Initialize a generator for a group of Meteorite objects."""
        self.random_state = random.Random(seed)
        self.seed = seed
        self.current_count = 1000

    def random_float_between(self, low, high):
        """Generate a random number between bounds low and high."""
        return ((high - low) * self.random_state.random()) + low

    def generate_meteorite_coeffs(self,
                                  c_pos_x_bounds, c_vel_x_bounds, c_accel_bounds,
                                  c_pos_y_bounds, c_vel_y_bounds, t_start, count):
        """Generate random coefficients for Meteorite motion."""
        coeff = ({
            'c_pos_x': self.random_float_between(*c_pos_x_bounds),
            'c_vel_x': self.random_float_between(*c_vel_x_bounds),
            'c_accel': self.random_float_between(*c_accel_bounds),
            'c_pos_y': self.random_float_between(*c_pos_y_bounds),
            'c_vel_y': self.random_float_between(*c_vel_y_bounds),
            't_start': t_start,
            'id': count,
        })
        return coeff

    def generate(self, t_past, t_future, t_step,
                 turret,
                 arena,
                 c_pos_bound=0.0001,
                 c_vel_bound=0.001,
                 c_accel_bound=MAX_MAGNITUDE_ACCEL,
                 meteorite_seed=0,
                 min_dist=0.03,
                 y_init_bounds=(-0.7, 0.8)):
        """Generate Meteorite coefficients over time."""
        x_bound_coe = 0.4
        overall_x_pos_bounds = (-c_pos_bound * x_bound_coe,  c_pos_bound * x_bound_coe)
        overall_x_vel_bounds = (-c_vel_bound * x_bound_coe, c_vel_bound * x_bound_coe)

        c_pos_y_bounds = (-c_pos_bound, c_pos_bound)
        c_vel_y_bounds = (-c_vel_bound, -TEENSY_COEFFICIENT*c_vel_bound)
        c_accel_almostzero = TEENSY_COEFFICIENT
        if c_accel_bound == 0.:
            c_accel_almostzero = 0.0
        accel_bounds = (-c_accel_bound, c_accel_almostzero)

        meteorites = []

        def meteorite_init_location_bad(coes):
            tmp_meteorite = Meteorite(coes, ACCEL_CORR_FACTOR_S, LASER_LENGTH)
            xypos = tmp_meteorite.xy_pos(0)
            # print('Testing: (x, y) is ({}, {})'.format(xypos[0], xypos[1]))
            return (xypos[0] <= arena.x_bounds[0]) or \
                (xypos[0] >= arena.x_bounds[1]) or \
                (xypos[1] < y_init_bounds[0]) or \
                (xypos[1] > y_init_bounds[1])
            # the last condition here is to prevent meteorites from
            # generating very close to the ground

        for t in range(t_past, t_future):

            if not (t % t_step):
                regenerate = True
                while regenerate:
                    coeffs = self.generate_meteorite_coeffs(overall_x_pos_bounds,
                                                            overall_x_vel_bounds,
                                                            accel_bounds,
                                                            c_pos_y_bounds,
                                                            c_vel_y_bounds,
                                                            t,
                                                            self.current_count)
                    regenerate = meteorite_init_location_bad(coeffs)
                self.current_count += 1

                a = Meteorite(coeffs, ACCEL_CORR_FACTOR_S, LASER_LENGTH)
                meteorites.append(a)

        return MeteorShower(arena, self.seed, P_HIT, LASER_LENGTH, meteorites,
                            turret, min_dist)

def args_as_dict(args):
    if isinstance(args, dict):
        return args
    elif isinstance(args, argparse.Namespace):
        return vars(args)
    else:
        raise RuntimeError('cannot convert to dict: %s' % str(args))

def args_as_namespace(args):
    if isinstance(args, dict):
        return argparse.Namespace(**args)
    elif isinstance(args, argparse.Namespace):
        return args
    else:
        raise RuntimeError('cannot convert to namespace: %s' % str(args))


def params(args):
    """Process arguments and set up the environment."""
    my_args = args_as_namespace(args)

    field_generator = MeteorShowerGenerator(seed=my_args.seed)

    dummy_arena = arena.Arena()
    laser_state = {'h': math.pi * 0.5,
                   'hp': my_args.turret_hp,
                   'laser_shots_remaining': my_args.num_laser_shots}

    dummy_turret = Turret({'x': my_args.turret_x, 'y': -1.0},
                          my_args.max_angle_change,
                          my_args.dt)

    field = field_generator.generate(t_past=my_args.t_past,
                                     t_future=my_args.t_future,
                                     t_step=my_args.t_step,
                                     turret=dummy_turret,
                                     arena=dummy_arena,
                                     c_pos_bound=my_args.meteorite_c_pos_max,
                                     c_vel_bound=my_args.meteorite_c_vel_max,
                                     c_accel_bound=my_args.meteorite_c_accel_max,
                                     meteorite_seed=my_args.seed,
                                     min_dist=my_args.min_dist,
                                     y_init_bounds=(
                                         my_args.min_y_init,
                                         my_args.max_y_init))

    return {"meteorites": [dict(a.params) for a in field.meteorites],
            "initial_laser_state": laser_state,
            "accel_corr_factor_s": ACCEL_CORR_FACTOR_S,
            "prob_hit_destroys": P_HIT,
            "num_laser_shots": my_args.num_laser_shots,
            "laser_effectiveness_distance": LASER_LENGTH,
            "in_bounds": dict(IN_BOUNDS),
            "min_dist": my_args.min_dist,
            "noise_sigma_x": my_args.noise_sigma_x,
            "noise_sigma_y": my_args.noise_sigma_y,
            "nsteps": my_args.nsteps,
            "dt": my_args.dt,
            "_args": vars(my_args)}


def main(args):
    """Set up parameters and run the simulation."""
    p = params(args=args)

    with open(f'{args.outfile}.json', 'w+') as f:
        json.dump(p, f, indent=2)

    print("Wrote %s" % args.outfile)


def parser():
    """Parse arguments."""
    prsr = argparse.ArgumentParser("Generate parameters for a test case and write them to file.")
    prsr.add_argument("outfile",
                      help="name of file to write (the .json extension will be appended to this name)")
    prsr.add_argument("--turret_x",
                      help="X-location of turret (should be in the range (-1.0, 1.0))",
                      type=float,
                      default=0.0)
    prsr.add_argument("--turret_hp",
                      help="Turret's initial health point count",
                      type=int,
                      default=50)
    prsr.add_argument("--num_laser_shots",
                      help="Initial number of laser shots turret can fire",
                      type=int,
                      default=50)
    prsr.add_argument("--t_past",
                      help="time in past (negative integer) from which to start generating meteorites",
                      type=int,
                      default=-100)
    prsr.add_argument("--t_future",
                      help="time into future (positive integer) at which to stop generating meteorites",
                      type=int,
                      default=400)
    prsr.add_argument("--t_step",
                      help="add a meteorite every N-th time step",
                      type=int,
                      default=1)
    prsr.add_argument("--noise_sigma_x",
                      help="sigma of Gaussian noise applied to the x-component of meteorite measurements",
                      type=float,
                      default=0.045)
    prsr.add_argument("--noise_sigma_y",
                      help="sigma of Gaussian noise applied to the y-component of meteorite measurements",
                      type=float,
                      default=0.075)
    prsr.add_argument("--min_y_init",
                      help="Lowest initial meteorite y-coordinate",
                      type=float,
                      default=-0.7)
    prsr.add_argument("--max_y_init",
                      help="Maximum initial meteorite y-coordinate",
                      type=float,
                      default=2.5)
    prsr.add_argument("--nsteps",
                      help="Number of timesteps to simulate",
                      type=int,
                      default=500)
    prsr.add_argument("--dt",
                      help="Duration of a single timestep",
                      type=float,
                      default=0.1)
    prsr.add_argument("--meteorite_c_pos_max",
                      help="maximum magnitude for meteorite position term coefficient",
                      type=float,
                      default=0.001)
    prsr.add_argument("--meteorite_c_vel_max",
                      help="maximum magnitude for meteorite velocity term coefficient",
                      type=float,
                      default=0.05)
    prsr.add_argument("--meteorite_c_accel_max",
                      help="maximum magnitude for meteorite acceleration term coefficient",
                      type=float,
                      default=MAX_MAGNITUDE_ACCEL)
    prsr.add_argument("--min_dist",
                      help="minimum distance estimate must be from meteorite location to be considered correct; also, if a laser comes within this distance of a meteorite, the meteorite is destroyed with p=0.75.",
                      type=float,
                      default=0.02)
    prsr.add_argument("--max_angle_change",
                      help="maximum increment of the laser's angle, in radians",
                      type=float,
                      default=np.pi/15.0)
    prsr.add_argument("--seed",
                      help="random seed to use when generating meteorites",
                      type=int,
                      default=0)
    return prsr


if __name__ == '__main__':
    args = parser().parse_args()
    main(args)
