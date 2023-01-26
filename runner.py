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

import math
import random

ESTIMATE_ACCURACY_THRESHOLD = 0.9
INIT_IMMUNITY_DTS = 5
LASER_RIGHT_ANGLE = 0.0
LASER_LEFT_ANGLE = math.pi


def l2(xy0, xy1):
    """Compute the L2 norm (distance) between points xy0 and xy1."""
    dx = xy0[0] - xy1[0]
    dy = xy0[1] - xy1[1]
    return math.sqrt((dx * dx) + (dy * dy))


def clamp(value, lower, upper):
    """Clamp value to be in the range [lower, upper].

    This function is from this StackOverflow answer:
    https://stackoverflow.com/questions/9775731/clamping-floating-numbers-in-python/58470178#58470178
    """
    # Beginning of code from
    # https://stackoverflow.com/questions/9775731/clamping-floating-numbers-in-python/58470178#58470178
    return lower if value < lower else upper if value > upper else value
    # End of code from
    # https://stackoverflow.com/questions/9775731/clamping-floating-numbers-in-python/58470178#58470178


class BaseRunnerDisplay(object):
    """Base class for procedure runners."""

    def setup(self, x_bounds, y_bounds,
              in_bounds,
              margin,
              noise_sigma_x,
              noise_sigma_y,
              turret,
              num_laser_shots,
              max_angle_change):
        """Create base class version of fcn to initialize procedure runner."""
        pass

    def begin_time_step(self, t):
        """Create base class version of timestep start for procedure runner."""
        pass

    def meteorite_at_loc(self, i, x, y):
        pass

    def meteorite_estimated_at_loc(self, i, x, y, is_match=False):
        pass

    def meteorite_estimates_compared(self, num_matched, num_total):
        pass

    def turret_at_loc(self, h, laser_len=None):
        pass

    def laser_target_heading(self, rad, laser_len):
        pass

    def estimation_done(self, retcode, t):
        pass

    def end_time_step(self, t):
        pass

    def teardown(self):
        pass

    def laser_destruct(self):
        pass


SUCCESS = 'success'
FAILURE_TOO_MANY_STEPS = 'too_many_steps'
FAILURE_HIT_GROUND = 'meteorite_hit_ground'

# Custom failure states for defense.
DEF_FAILURE = 'explosion'


def add_observation_noise(meteorite_locations, noise_sigma_x=0.0,
                          noise_sigma_y=0.0, random_state=None):
    """Add noise to meteorite observations."""
    my_random_state = random_state if random_state else random.Random(0)
    ret = ()
    for i, x, y in meteorite_locations:
        err_x = my_random_state.normalvariate(mu=0.0, sigma=noise_sigma_x)
        err_y = my_random_state.normalvariate(mu=0.0, sigma=noise_sigma_y)
        ret += ((i, x + err_x, y + err_y),)
    return ret


class MalformedEstimate(Exception):
    """Raise this type of exception if an estimate is not a three-tuple."""
    pass


def validate_estimate(tpl):
    """Ensure that estimate of meteorite location is valid."""
    try:
        i, x, y = tpl
        return (int(i), float(x), float(y))
    except (ValueError, TypeError) as e:
        raise MalformedEstimate('Estimated location %s should be of the form (i, x, y), a tuple with type (int, float, float) or equivalent numpy types.' % str(tpl))


def run_estimation(field,
                   in_bounds,
                   noise_sigma_x,
                   noise_sigma_y,
                   min_dist,
                   turret,
                   turret_init_health,
                   num_laser_shots,
                   max_angle_change,
                   nsteps,
                   dt,
                   seed,
                   display=None):
    """Run the estimation procedure."""
    ret = (FAILURE_TOO_MANY_STEPS, nsteps)
    num_steps_gt_90pct = 0

    num_req_timesteps_estimates_gt_90pct = 10
    if noise_sigma_x <= 0.0 and noise_sigma_y <= 00:
        # Estimation Part 1A--no noise case
        num_req_timesteps_estimates_gt_90pct = 75

    random_state = random.Random(seed)

    display.setup(field.x_bounds, field.y_bounds,
                  in_bounds,
                  margin=min_dist,
                  noise_sigma_x=noise_sigma_x,
                  noise_sigma_y=noise_sigma_y,
                  turret=turret,
                  num_laser_shots=num_laser_shots,
                  max_angle_change=max_angle_change)

    estimated_locs = ()  # estmated locations

    turret_quantities = {'turret_x': turret.x_pos,
                         'turret_y': turret.y_pos}

    for timesteps in range(0, nsteps):
        turret.x_pos = turret_quantities['turret_x']
        turret.y_pos = turret_quantities['turret_y']
        t = timesteps * dt
        display.begin_time_step(t)

        # time t's true meteorite locations
        meteorite_coordinates = field.meteorite_locations(t)

        # if the following condition evaluates to True, either the
        # predict_from_observations function in the Turret class has not been
        # implemented yet, or the return value of predict_from_observations has
        # not yet been replaced with meteorite location estimates
        # (If you get this error, look at the return statements in your
        # predict_from_observations function--are they what you intend to return?)
        if t < 0.2 and estimated_locs == ((1, 0.5, 0.5),):
            print('Please implement the Turret class\'s predict_from_observations function!')

        actual = {}
        matches = ()

        # display meteorites
        for i, x, y in meteorite_coordinates:
            if i == -1:
                continue
            display.meteorite_at_loc(i, x, y)
            actual[i] = (x, y)

        estimated_locs_seen = set()

        # since Turret's predict_from_observations is predicting the meteorites'
        # locations at time t+1, compare the meteorite location estimates
        # generated on the previous iteration of this loop with the current
        # true meteorite locations
        for tpl in estimated_locs:

            # make sure estimates are in the correct format
            i, x, y = validate_estimate(tpl)

            # ignore duplicate entries
            if i in estimated_locs_seen:
                continue
            # ignore meteorites with IDs of -1 (destroyed or hit the ground)
            if i == -1:
                continue

            # mark meteorite i as seen
            estimated_locs_seen.add(i)

            # if meteorite i exists in the true meteorite locations
            if i in actual:
                # compute the distance between the meteorite's estimated
                # location and its true location
                dist = l2((x, y), actual[i])
                # consider the estimate to be a match if distance between true
                # and estimate location are less than min_dist
                is_match = (dist < min_dist)
                if is_match:
                    matches += (i,)
            else:
                is_match = False

            # display estimated meteorites
            display.meteorite_estimated_at_loc(i, x, y, is_match)

        display.meteorite_estimates_compared(len(matches), len(actual))

        display.end_time_step(t)
        # If time t's estimates were good enough, we're done.
        if len(matches) >= len(actual) * ESTIMATE_ACCURACY_THRESHOLD:
            num_steps_gt_90pct += 1
        else:
            num_steps_gt_90pct = 0
        if num_steps_gt_90pct >= num_req_timesteps_estimates_gt_90pct:
            ret = (SUCCESS, t)
            break

        # estimated meteorite locations for time t+1
        # (these will be the estimated_locs evaluated for accuracy next
        # timestep)
        estimated_locs = turret.predict_from_observations(
                add_observation_noise(meteorite_coordinates, noise_sigma_x,
                                      noise_sigma_y, random_state))

    display.estimation_done(*ret)
    display.teardown()
    return ret


def run_defense(field,
                in_bounds,
                noise_sigma_x,
                noise_sigma_y,
                min_dist,
                turret,
                turret_init_health,
                num_laser_shots,
                max_angle_change,
                nsteps,
                dt,
                seed,
                display=None):
    """Run defense procedure."""
    ret = (DEF_FAILURE, nsteps)
    random_state = random.Random(seed)

    display.setup(field.x_bounds, field.y_bounds,
                  in_bounds,
                  margin=min_dist,
                  noise_sigma_x=noise_sigma_x,
                  noise_sigma_y=noise_sigma_y,
                  turret=turret,
                  num_laser_shots=num_laser_shots,
                  max_angle_change=max_angle_change)

    initial_laser_shots = num_laser_shots

    turret_quantities = {'turret_health': turret_init_health,
                         'laser_shots_remaining': num_laser_shots,
                         'turret_x': turret.x_pos,
                         'turret_y': turret.y_pos}

    # This makes meteorites that are below the "hit" boundary before time
    # starts go away before the turret's health can be affected
    field.laser_or_ground_hit(INIT_IMMUNITY_DTS, 0,
                              turret_quantities['laser_shots_remaining'],
                              False)

    # Set the current laser angle to its initial value
    laser_angle_rad = math.pi * 0.5
    laser_is_on = False

    for timesteps in range(0, nsteps):
        turret.x_pos = turret_quantities['turret_x']
        turret.y_pos = turret_quantities['turret_y']
        t = timesteps * dt
        display.begin_time_step(t)

        # get true meteorite locations at time t
        meteorite_coordinates = field.meteorite_locations(t)
        for i, x, y in meteorite_coordinates:
            if i == -1:
                continue
            display.meteorite_at_loc(i, x, y)

        # if no meteorites left, break out of simulation
        # but meteorite_coordinates usually still contains some -1 ID
        # meteorites even in the latter phases of simulation, so triggering
        # this condition should be unlikely
        if not meteorite_coordinates:
            break

        # if turret decided to fire in previous timestep, fire and decrement
        # laser shots, and prepare values for display at time t (TIME t)
        if laser_is_on and turret_quantities['laser_shots_remaining'] > 0:
            display.laser_target_heading(laser_angle_rad,
                                         field.laser_effectiveness_distance)
            turret_quantities['laser_shots_remaining'] -= 1

        # after laser's time t fires/motions (decided in previous timestep),
        # check whether the laser will hit any meteorites at time t, and check
        # whether meteorites hit the ground at time t
        # for any meteorites that hit the ground, record health loss
        health_loss = field.laser_or_ground_hit(t, laser_angle_rad,
                                                turret_quantities['laser_shots_remaining'],
                                                laser_is_on)
        # the turret only loses health when a meteorite hits the ground after
        # the simulation has executed INIT_IMMUNITY_DTS timesteps
        if t > INIT_IMMUNITY_DTS:
            # if we are past the immunity period of INIT_IMMUNITY_DTS
            # timesteps, deduct one health point for each meteorite that hits
            # the ground
            turret_quantities['turret_health'] -= health_loss

        # display the still-alive meteorites in the GUI for time t (TIME t)
        for i, x, y in meteorite_coordinates:
            if i == -1:
                continue
            display.meteorite_at_loc(i, x, y)

        # if turret health has reached 0 or below at time t, explode turret and
        # prepare to return failure
        if turret_quantities['turret_health'] <= 0:
            display.laser_destruct()
            ret = (DEF_FAILURE, t)
            display.end_time_step(t)
            break

        # display the turret, its angle/firing status, and its health points at
        # time t (TIME t)
        display.turret_health(turret_quantities['turret_health'],
                              turret_init_health)
        display.turret_fire_status(turret_quantities['laser_shots_remaining'],
                                   initial_laser_shots)
        display.turret_at_loc(laser_angle_rad)

        # turret estimating meteorite locations for time t + 1, using the noisy
        # observations taken at time t
        estimated_locs = turret.predict_from_observations(
                add_observation_noise(meteorite_coordinates, noise_sigma_x,
                                      noise_sigma_y, random_state))
        # make sure turret.predict_from_observations is not returning default
        # values, and if it is, tell the user to implement predict_from_observations
        # and return correct estimates
        if t < 0.2 and estimated_locs == ((1, 0.5, 0.5),):
            print('Please implement the Turret class\'s predict_from_observations function!')

        # update laser_angle_rad for turret's aim in timestep t
        laser_action = turret.get_laser_action(laser_angle_rad)

        if isinstance(laser_action, float) or isinstance(laser_action, int):
            # if laser_action is a float or int, interpret it as the change
            # in the laser's aim angle (in radians) and add it to the
            # laser's previous angle (time t)
            laser_is_on = False
            laser_angle_change = float(laser_action)
            # if abs value of change angle is greater than allowed, keep
            # the same sign, but reduce change angle to max_angle_change
            if abs(laser_angle_change) > max_angle_change:
                laser_angle_change = math.copysign(max_angle_change,
                                                   laser_angle_change)
            # Clip laser angle to within allowed bounds
            laser_angle_rad = clamp(laser_angle_rad + laser_angle_change,
                                    LASER_RIGHT_ANGLE,
                                    LASER_LEFT_ANGLE)
        elif isinstance(laser_action, str):
            # If the laser's action is a string, if the string is 'fire',
            # don't move the laser, but fire it (time t)
            if 'fire' in laser_action.lower():
                laser_is_on = True
        else:
            print('Invalid return value from Turret.get_laser_action: {}.'.format(laser_action))
            print('Please ensure that get_laser_action returns a float, int, or string. Exiting.')
            turret_quantities['turret_health'] = 0
            break

        display.end_time_step(t)

    # we have reached the end of simulation time, so if the turret is not dead,
    # this case was a success
    if turret_quantities['turret_health'] > 0:
        ret = (SUCCESS, t)

    display.teardown()
    return ret
