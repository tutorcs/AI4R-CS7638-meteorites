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

import time
import turtle
import runner


# Set DEBUG_DISPLAY to True to see the meteorite ID numbers and the labels of
# the corners of the arena in the GUI, or set it to FALSE to not show those
# values
DEBUG_DISPLAY = True


class TurtleRunnerDisplay(runner.BaseRunnerDisplay):
    """Handle GUI display of the Meteorites project simulation."""

    def __init__(self, width, height):
        """Initialize the turtle display."""
        self.width = width
        self.height = height
        self.x_bounds = (0.0, 1.0)
        self.y_bounds = (0.0, 1.0)
        self.meteorite_turtles = {}
        self.estimated_meteorite_turtles = {}
        self.turret_turtle = turtle.Turtle()
        self.turret_turtle.radians()
        self.laser_turtle = turtle.Turtle()
        self.laser_turtle.radians()
        self.laser_shots_remaining_turtle = turtle.Turtle()
        self.laser_shots_remaining_turtle.radians()
        self.turret_loc = {}
        self.time_turtle = turtle.Turtle()
        self.meteorite_size = 0.3

    def setup(self, x_bounds, y_bounds,
              in_bounds,
              margin,
              noise_sigma_x,
              noise_sigma_y,
              turret,
              num_laser_shots,
              max_angle_change):
        """Initialize necessary turtles and their properties."""
        self.x_bounds = x_bounds
        self.y_bounds = y_bounds
        self.margin = margin
        xmin, xmax = x_bounds
        ymin, ymax = y_bounds
        dx = xmax - xmin
        dy = ymax - ymin
        turtle.setup(width=self.width, height=self.height, starty=50)
        turtle.setworldcoordinates(xmin - (dx * margin),
                                   ymin - (dy * margin),
                                   xmax + (dx * margin),
                                   ymax + (dy * margin))
        turtle.tracer(0, 1)
        self._draw_inbounds(in_bounds)

        self.turret_turtle.penup()
        self.turret_turtle.shape("classic")
        self.turret_turtle.color("black")
        self.turret_turtle.shapesize(self.margin * 10, self.margin * 10)
        self.turret_loc['x_coord'] = turret.x_pos
        self.turret_loc['y_coord'] = turret.y_pos
        self.turret_turtle.setposition(self.turret_loc['x_coord'],
                                       self.turret_loc['y_coord'])
        self.time_turtle.penup()
        self.time_turtle.setposition(self.turret_loc['x_coord'] + 0.3,
                                     self.turret_loc['y_coord'])
        self.time_turtle.shape("circle")
        self.time_turtle.shapesize(0.0001 * self.margin, 0.0001 * self.margin)
        self.laser_shots_remaining_turtle.penup()
        self.laser_shots_remaining_turtle.setposition(self.turret_loc['x_coord'] - 0.5,
                                                      self.turret_loc['y_coord'])
        self.laser_shots_remaining_turtle.shape("circle")
        self.laser_shots_remaining_turtle.shapesize(0.0001 * self.margin, 0.0001 * self.margin)

    def _draw_inbounds(self, in_bounds):
        """Draw the bounds of the simulation world."""
        t = turtle.Turtle()
        t.hideturtle()
        t.shapesize(0.00001, 0.00001)
        t.pencolor("black")
        t.penup()
        t.setposition(in_bounds.x_bounds[0], in_bounds.y_bounds[0])
        t.pendown()
        t.setposition(in_bounds.x_bounds[1], in_bounds.y_bounds[0])
        if DEBUG_DISPLAY:
            t._write('({}, {})'.format(in_bounds.x_bounds[1], in_bounds.y_bounds[0]), 'center', 'arial')
        t.setposition(in_bounds.x_bounds[1], in_bounds.y_bounds[1])
        if DEBUG_DISPLAY:
            t._write('({}, {})'.format(in_bounds.x_bounds[1], in_bounds.y_bounds[1]), 'center', 'arial')
        t.setposition(in_bounds.x_bounds[0], in_bounds.y_bounds[1])
        if DEBUG_DISPLAY:
            t._write('({}, {})'.format(in_bounds.x_bounds[0], in_bounds.y_bounds[1]), 'center', 'arial')
        t.setposition(in_bounds.x_bounds[0], in_bounds.y_bounds[0])
        if DEBUG_DISPLAY:
            t._write('({}, {})'.format(in_bounds.x_bounds[0], in_bounds.y_bounds[0]), 'center', 'arial')
        t.showturtle()

    def begin_time_step(self, t):
        """Set up turtles for the beginning of current timestep t."""
        self.time_turtle.clear()
        self.time_turtle.hideturtle()
        self.time_turtle._write("Time: {0:.1f}".format(t), 'center', 'arial')
        for idx, trtl in list(self.meteorite_turtles.items()):
            trtl.clear()
            trtl.hideturtle()
        for idx, trtl in list(self.estimated_meteorite_turtles.items()):
            trtl.clear()
            trtl.hideturtle()
        self.turret_turtle.clear()
        self.turret_turtle.hideturtle()
        self.laser_turtle.clear()
        self.laser_turtle.hideturtle()
        self._laser_go_home()

    def meteorite_at_loc(self, i, x, y):
        """Display meteorite at provided location."""
        if i < 0:
            # meteorite is deactivated; don't show
            return
        if i not in self.meteorite_turtles:
            trtl = turtle.Turtle()
            trtl.shape("circle")
            trtl.color("grey")
            trtl.shapesize(self.meteorite_size, self.meteorite_size)
            trtl.penup()
            self.meteorite_turtles[i] = trtl
        self.meteorite_turtles[i].setposition(x, y)
        # Set DEBUG_DISPLAY to True to show meteorite IDs
        if DEBUG_DISPLAY:
            self.meteorite_turtles[i]._write(str(i), 'center', 'arial')
        self.meteorite_turtles[i].showturtle()

    def meteorite_estimated_at_loc(self, i, x, y, is_match=False):
        """Display meteorite estimate at provided location.

        Meteorite will be colored green if it is close enough to the
        meteorite's true position to be counted as correct, and will be colored
        red otherwise.
        """
        if i < 0:
            # meteorite is deactivated; don't show
            return
        if i not in self.estimated_meteorite_turtles:
            trtl = turtle.Turtle()
            trtl.shape("circle")
            trtl.color("#88ff88" if is_match else "#aa4444")
            trtl.shapesize(self.meteorite_size, self.meteorite_size)
            trtl.penup()
            self.estimated_meteorite_turtles[i] = trtl
        self.estimated_meteorite_turtles[i].color("#88ff88" if is_match else "#aa4444")
        self.estimated_meteorite_turtles[i].setposition(x, y)
        self.estimated_meteorite_turtles[i].showturtle()

    def turret_at_loc(self, hdg):
        """Display the turret."""
        if hdg is not None:
            self.turret_turtle.setheading(hdg)
            self.turret_turtle.shapesize(2, 2)
        self.turret_turtle.showturtle()

    def turret_health(self, hp, hp0):
        """Display the turret's current health."""
        self.turret_turtle._write("{0}/{1} HP".format(int(hp), int(hp0)), 'center', 'arial')

    def turret_fire_status(self, laser_shots_remaining, initial_laser_shots):
        """Display the number of remaining shots the turret can fire."""
        self.laser_shots_remaining_turtle.clear()
        self.laser_shots_remaining_turtle.hideturtle()
        self.laser_shots_remaining_turtle._write("\nShots Remaining: {0}/{1}".format(
            int(laser_shots_remaining),
            int(initial_laser_shots)), 'center', 'arial')
        self.laser_shots_remaining_turtle.showturtle()

    def laser_target_heading(self, rad, laser_len):
        """Draw the turret's laser fire with given heading and length."""
        self._laser_go_home()
        self.laser_turtle.color("red")
        self.laser_turtle.setheading(rad)
        self.laser_turtle.pendown()
        self.laser_turtle.forward(laser_len)
        self.laser_turtle.penup()
        self.laser_turtle.showturtle()

    def end_time_step(self, t):
        """Update GUI for the end of a timestep."""
        turtle.update()
        time.sleep(0.1)

    def teardown(self):
        """Conclude the GUI visualization of the simulation."""
        turtle.done()

    def laser_destruct(self):
        """Draw the explosion of the turret."""
        self.turret_turtle.shape("circle")
        self.turret_turtle.shapesize(10, 10)
        self.turret_turtle.color("orange")

    def _laser_go_home(self):
        """Send laser's turtle back to its home location, but keep heading."""
        self.laser_turtle.setposition(self.turret_loc['x_coord'],
                                      self.turret_loc['y_coord'])
