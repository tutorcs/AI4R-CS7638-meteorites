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

# python modules
import argparse
import importlib
import os.path
import sys

# project files
import traceback

import meteorite
import arena
from turret import Turret
import runner
import json

def load_cases():
    cases = {}
    base_dir = 'cases'
    for case_file in sorted(os.listdir(base_dir)):
        if case_file.endswith('.json'):
            case_id = os.path.splitext(os.path.basename(case_file))[0]
            with open(os.path.join(base_dir, case_file)) as f:
                cases[case_id] = json.load(f)
    return cases

cases = load_cases()

from text_display import TextRunnerDisplay
try:
    from turtle_display import TurtleRunnerDisplay
except ImportError as e:
    sys.stderr.write('turtle display not available, using text instead\n')
    TurtleRunnerDisplay = lambda h, w: TextRunnerDisplay()

TURRET_INITIAL_POS = {'x': 0.0,
                      'y': -1.0}


def display_for_name(dname):
    """Set up desired display tupe."""
    if dname == 'turtle':
        return TurtleRunnerDisplay(800, 800)
    elif dname == 'text':
        return TextRunnerDisplay()
    else:
        return runner.RunnerDisplay()


def case_params(case_num):
    """Get the parameters for the given case."""
    case_id = f'case{case_num}' if isinstance(case_num, int) else case_num
    return cases[case_id]


def run_method(method_name):
    """Convert input method into the function needed to run that method."""
    if method_name == 'estimate':
        return runner.run_estimation
    elif method_name == 'defense':
        return runner.run_defense
    elif method_name == 'kf_nonoise':
        return runner.run_estimation
    else:
        raise RuntimeError('unknown method %s' % method_name)


def run_kwargs(params):
    """Set up kwargs for running main."""
    meteorites = []
    for themeteorite in params['meteorites']:
        meteorites.append(
            meteorite.Meteorite(themeteorite,
                                params['accel_corr_factor_s'],
                                params['laser_effectiveness_distance']))

    in_bounds = arena.Arena()
    turret = Turret(TURRET_INITIAL_POS,
                    params['_args']['max_angle_change'],
                    params['dt'])

    ret = {'field': meteorite.MeteorShower(in_bounds, params['_args']['seed'],
                                           params['prob_hit_destroys'],
                                           params['laser_effectiveness_distance'],
                                           meteorites, turret,
                                           params['min_dist']),
           'in_bounds': in_bounds,
           'noise_sigma_x': params['noise_sigma_x'],
           'noise_sigma_y': params['noise_sigma_y'],
           'min_dist': params['min_dist'],
           'turret': turret,
           'turret_init_health': params['initial_laser_state']['hp'],
           'num_laser_shots': params['num_laser_shots'],
           'max_angle_change': params['_args']['max_angle_change'],
           'nsteps': params['_args']['nsteps'],
           'dt': params['_args']['dt'],
           'seed': params['_args']['seed']}

    return ret


def main(method_name, case_id, display_name):
    """Run the specified case using the specified method."""
    if case_id.isdigit():
        case_id = 'case'+case_id
    try:
        params = cases[case_id]
    except Exception as e:
        print(f'fUnable to load test case: "{case_id}.json"')
        return

    import timeit
    start = timeit.default_timer()
    retcode, t = run_method(method_name)(display=display_for_name(display_name),
                                         **(run_kwargs(params)))
    stop = timeit.default_timer()
    print(f'Approximate run time: {stop - start} seconds')
    print((retcode, t))


def parser():
    """Parse command-line arguments."""
    prsr = argparse.ArgumentParser()
    prsr.add_argument('method',
                      help="Which method to test",
                      type=str,
                      choices=('kf_nonoise', 'estimate', 'defense'),
                      default='estimate')
    prsr.add_argument('--case',
                      help="test case id (one of %s) (just number is ok if test case begins with 'case') or test case file" % list(cases.keys()),
                      type=str,
                      default=1)
    prsr.add_argument('--display',
                      choices=('turtle', 'text', 'none'),
                      default='none')
    return prsr


if __name__ == '__main__':
    args = parser().parse_args()
    if 'none' in args.display:
        gui_runcom = sys.argv
        gui_runcom.insert(-1, '--display turtle')
        thecommand = '    python ' + ' '.join(gui_runcom)
        print('No display method provided in run command; defaulting to \'text\'.')
        print('To re-run this simulation with the GUI visualization, please run the command\n')
        print(thecommand + '\n')
        args.display = 'text'
    main(method_name=args.method,
         case_id=args.case,
         display_name=args.display)
