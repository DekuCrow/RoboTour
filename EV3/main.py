#! /usr/bin/env python3
# Core imports
import time
import sys
import ev3dev.ev3 as ev3
from urllib.request import urlopen
import re
from threading import Thread
from sensor_hub import *
from comms import *
from dijkstra import *

import cProfile
pr = cProfile.Profile()


# ###################### GLOBAL VARIABLE ####################
obstacle_detection_distance = 200  # in mm
side_distance = 17
link = "http://www.mahbubiftekhar.co.uk/receiver.php"
pointerState = ""
startPosition = '10'  # Toilet
robot_location = startPosition
robot_orientation = 'N'  # N,S,W,E (North South West East)
robot_pointer = 'N'  # N,S,W,E (North of the robot)
orientation_map = dict()  # Map for Orientation between neighbouring points
dijkstra_map = dict()  # Map for Distance between neighbouring points
motor_map = dict()
art_pieces_map = dict()
obstacle_map = dict()
# Base speed for Line Following
default_speed = 100
is_stop = False
is_skip = False
is_toilet = False
is_exit = False
is_cancel = False

branch_skip = False

###############################################################

# ###################### INITIALISING MAP #############################


def initialising_map():
    # Orientation from point X to Y is N/S/W/E
    # 38 edges in total
    global orientation_map
    orientation_map[('0', '1')] = "S"
    orientation_map[('0', '8')] = "N"
    orientation_map[('1', '12')] = "S"
    orientation_map[('1', '0')] = "N"
    orientation_map[('2', '15')] = "N"
    orientation_map[('2', '3')] = "S"
    orientation_map[('3', '2')] = "N"
    orientation_map[('3', '13')] = "S"
    orientation_map[('4', '11')] = "S"
    orientation_map[('4', '14')] = "N"
    orientation_map[('5', '14')] = "WS"  # Special Case
    orientation_map[('5', '6')] = "E"
    orientation_map[('6', '5')] = "W"
    orientation_map[('6', '7')] = "E"
    orientation_map[('7', '9')] = "ES"
    orientation_map[('7', '6')] = "W"
    orientation_map[('8', '0')] = "S"
    orientation_map[('8', '15')] = "E"
    orientation_map[('8', '14')] = "W"
    orientation_map[('9', '13')] = "SW"
    orientation_map[('9', '15')] = "W"
    orientation_map[('9', '7')] = "NW"
    orientation_map[('10', '11')] = "N"
    orientation_map[('11', '10')] = "S"
    orientation_map[('11', '4')] = "N"
    orientation_map[('11', '12')] = "E"
    orientation_map[('12', '13')] = "E"
    orientation_map[('12', '1')] = "N"
    orientation_map[('12', '11')] = "W"
    orientation_map[('13', '3')] = "N"
    orientation_map[('13', '9')] = "EN"
    orientation_map[('13', '12')] = "W"
    orientation_map[('14', '4')] = "S"
    orientation_map[('14', '8')] = "E"
    orientation_map[('14', '5')] = "NE"
    orientation_map[('15', '9')] = "E"
    orientation_map[('15', '2')] = "S"
    orientation_map[('15', '8')] = "W"

    # Distance Map for Dijkstra
    global dijkstra_map
    dijkstra_map = {
        '0': {'1': 26, '8': 21},
        '1': {'0': 26, '12': 19.5},
        '2': {'3': 26.5, '15': 19.5},
        '3': {'2': 26.5, '13': 20},
        '4': {'11': 33.5, '14': 31.5},
        '5': {'6': 27, '14': 46},
        '6': {'5': 27, '7': 28},
        '7': {'6': 28, '9': 46.5},
        '8': {'0': 21, '15': 31.5, '14': 28},
        '9': {'7': 46.5, '15': 32, '13': 85},
        '10': {'11': 20},
        '11': {'4': 33.5, '10': 20, '12': 28},
        '12': {'1': 19.5, '11': 28, '13': 32},
        '13': {'3': 20, '12': 32, '9': 85},
        '14': {'4': 31.5, '5': 46, '8': 28},
        '15': {'2': 19.5, '8': 31.5, '9': 32}

    }

    global motor_map
    motor_map = {
        '0': "E",
        '1': "W",
        '2': "E",
        '3': "W",
        '4': "E",
        '5': "S",
        '6': "S",
        '7': "N",
        '8': "N",
        '9': "E",
        'Exit': "S",
        'Toilet': "S"
    }

    global art_pieces_map
    art_pieces_map = {
        '0': "The Birth of Venus",
        '1': "The Creation of Adam",
        '2': "David",
        '3': "Girl with a Pearl Earring",
        '4': "Mona Lisa",
        '5': "Napoleon Crossing the Alps",
        '6': "The Starry Night",
        '7': "The Last Supper",
        '8': "The Great Wave of Kanagawa",
        '9': "Water Lilies",
        '10': "Exit",
        '12': "Toilet"
    }

    global obstacle_map
    obstacle_map[('10', '11')] = 'LEFT'
    obstacle_map[('11', '10')] = 'RIGHT'
    obstacle_map[('11', '12')] = 'RIGHT'
    obstacle_map[('12', '13')] = 'RIGHT'
    obstacle_map[('13', '12')] = 'LEFT'
    obstacle_map[('13', '9')] = 'RIGHT'
    obstacle_map[('9', '13')] = 'LEFT'
    obstacle_map[('9', '7')] = 'RIGHT'
    obstacle_map[('7', '9')] = 'LEFT'
    obstacle_map[('7', '6')] = 'RIGHT'
    obstacle_map[('6', '7')] = 'LEFT'
    obstacle_map[('6', '5')] = 'RIGHT'
    obstacle_map[('5', '6')] = 'LEFT'
    obstacle_map[('5', '14')] = 'RIGHT'
    obstacle_map[('14', '5')] = 'LEFT'
    obstacle_map[('14', '4')] = 'RIGHT'
    obstacle_map[('4', '14')] = 'LEFT'
    obstacle_map[('4', '11')] = 'RIGHT'
    obstacle_map[('11', '4')] = 'LEFT'


#####################################################################

# ###################### SETUP SENSORS ######################
hub = SensorHub()
sonar_front = ev3.UltrasonicSensor(ev3.INPUT_2)
sonar_front.mode = 'US-DIST-CM'  # Will return value in mm
sonar_left = HubSonar(hub, 's0')
sonar_right = HubSonar(hub, 's1')
motor_pointer = ev3.LargeMotor('outC')
motor_left = ev3.LargeMotor('outB')
motor_right = ev3.LargeMotor('outD')
colour_sensor_right = ev3.ColorSensor(ev3.INPUT_1)
colour_sensor_left = ev3.ColorSensor(ev3.INPUT_4)
colour_sensor_left.mode = 'COL-REFLECT'
colour_sensor_right.mode = 'COL-REFLECT'

white_threshold = 57
black_threshold = 10


if motor_pointer.connected & sonar_front.connected & motor_left.connected & motor_right.connected:
    print('All sensors and motors connected')
else:
    if not motor_pointer.connected:
        print("motorPointer not connected")
    if not sonar_front.connected:
        print("Sonar not connected")
    if not motor_left.connected:
        print("MotorLeft not connected")
    if not motor_right.connected:
        print("MotorRight not connected")
    if not colour_sensor_left.connected:
        print("ColorLeft not connected")
    if not colour_sensor_right.connected:
        print("ColorRight not connected")
    print('Please check all sensors and actuators are connected.')
    exit()

############################################################

# #################### SENSOR AND ACTUATOR FUNCTIONS ############################


def get_colour_right():
    return colour_sensor_right.value()


def get_colour_left():
    return colour_sensor_left.value()


def is_right_white_line_detected():  # Right Lego sensor
    # print('right: ', get_colour_right())
    return get_colour_right() > white_threshold


def is_left_white_line_detected():
    # print('left: ', get_colour_left())
    return get_colour_left() > white_threshold


def is_white_line_detected():
    return is_left_white_line_detected() or is_right_white_line_detected()


def is_not_white_line_detected():
    return (not is_left_white_line_detected()) or (not is_right_white_line_detected())


def is_left_black_line_detected():
    return get_colour_left() < black_threshold


def is_right_black_line_detected():
    return get_colour_right() < black_threshold


def is_black_line_detected():
    return is_left_black_line_detected() or is_right_black_line_detected()


def get_sonar_readings_front():
    return sonar_front.value()


def get_sonar_readings_left():
    return sonar_left.value()


def get_sonar_readings_right():
    return sonar_right.value()


def is_front_obstacle():
    return get_sonar_readings_front() < obstacle_detection_distance


def is_no_front_obstacle_lel():
    return get_sonar_readings_front() > obstacle_detection_distance * 1.5


def is_left_side_obstacle():
    return get_sonar_readings_left() < side_distance


def is_right_side_obstacle():
    return get_sonar_readings_right() < side_distance


def is_branch_detected(left, right):
    return (left > 60 and right > 60) or (left < 10 and right > 60)


def is_painting_detected():
    pass


def move_forward(speed, running_time):
    motor_left.run_timed(speed_sp=speed, time_sp=running_time)
    motor_right.run_timed(speed_sp=speed, time_sp=running_time)


def move_backward(speed, running_time):
    motor_left.run_timed(speed_sp=-speed, time_sp=running_time)
    motor_right.run_timed(speed_sp=-speed, time_sp=running_time)


def turn_right():

    motor_right.run_timed(speed_sp=-150, time_sp=700)
    motor_left.run_timed(speed_sp=250, time_sp=950)
    motor_left.wait_until_not_moving()
    motor_right.wait_until_not_moving()

    '''
    motor_right.run_timed(speed_sp=200, time_sp=150)
    motor_left.run_timed(speed_sp=200, time_sp=150)
    motor_right.wait_until_not_moving()
    motor_left.wait_until_not_moving()
    '''


def turn_left():
    motor_left.run_timed(speed_sp=-250, time_sp=850)
    motor_right.run_timed(speed_sp=150, time_sp=800)
    motor_left.wait_until_not_moving()
    motor_right.wait_until_not_moving()
    motor_left.run_timed(speed_sp=200, time_sp=150)
    motor_right.run_timed(speed_sp=200, time_sp=150)
    motor_left.wait_until_not_moving()
    motor_right.wait_until_not_moving()


def turn(left, right, running_time):  # For unclear speed
    motor_left.run_timed(speed_sp=left, time_sp=running_time)
    motor_right.run_timed(speed_sp=right, time_sp=running_time)


def turn_back():  # 180
    motor_left.run_timed(speed_sp=200, time_sp=2400)
    motor_right.run_timed(speed_sp=-200, time_sp=1200)
    motor_left.wait_until_not_moving()
    motor_right.wait_until_not_moving()


def turn_right_ninety():  # 90
    motor_left.run_timed(speed_sp=175, time_sp=1000)
    motor_right.run_timed(speed_sp=-175, time_sp=1000)
    wait_for_motor()


def turn_left_ninety():  # -90
    motor_left.run_timed(speed_sp=-175, time_sp=1000)
    motor_right.run_timed(speed_sp=175, time_sp=1000)
    wait_for_motor()


def turn_right_degree(degree):  # 90
    motor_left.run_timed(speed_sp=175, time_sp=degree*1000/90)
    motor_right.run_timed(speed_sp=-175, time_sp=degree*1000/90)
    wait_for_motor()


def turn_left_degree(degree):  # -90
    motor_left.run_timed(speed_sp=-175, time_sp=degree*1000/90)
    motor_right.run_timed(speed_sp=175, time_sp=degree*1000/90)
    wait_for_motor()


def stop_wheel_motor():
    motor_left.stop(stop_action="hold")
    motor_right.stop(stop_action="hold")


def wait_for_motor():
    motor_left.wait_until_not_moving()
    motor_right.wait_until_not_moving()


def speak(string):
    ev3.Sound.speak(string)


def turn_pointer_45(direction):  # Turn 45
    if direction == "CW":
        motor_pointer.run_timed(speed_sp=-414, time_sp=500)
        time.sleep(0.5)

    if direction == "ACW":
        motor_pointer.run_timed(speed_sp=414, time_sp=500)
        time.sleep(0.5)


def turn_pointer_180(direction):
    if direction == "CW":
        motor_pointer.run_timed(speed_sp=-414, time_sp=2000)
        time.sleep(2)

    if direction == "ACW":
        motor_pointer.run_timed(speed_sp=414, time_sp=2000)
        time.sleep(2)


def turn_and_reset_pointer(direction):
    if direction == "CW":
        turn_pointer_45("CW")
        turn_pointer_45("ACW")

    elif direction == "ACW":
        turn_pointer_45("ACW")
        turn_pointer_45("CW")


def point_to_painting(picture_id):
    if is_orientation_left(motor_map[picture_id]):
        turn_pointer_45("ACW")
        global robot_pointer
        robot_pointer = 'W'
    elif is_orientation_right(motor_map[picture_id]):
        turn_pointer_45("CW")
        global robot_pointer
        robot_pointer = 'E'
    elif is_orientation_back(motor_map[picture_id]):
        turn_pointer_180('CW')
        global robot_pointer
        robot_pointer = 'S'
    else:
        pass


def turn_back_pointer():
    if robot_pointer == 'S':
        turn_pointer_180('ACW')
    elif robot_pointer == 'W':
        turn_pointer_45("CW")
    elif robot_pointer == 'E':
        turn_pointer_45("ACW")
    else:
        pass

    global robot_pointer
    robot_pointer = 'N'

######################################################################

# ###################### ROBOTOUR FUNCTIONS ###########################


def get_closest_painting(d_map, location, pictures_lists):
    shortest_distance = sys.maxsize
    short_path = None
    closed_painting = None
    for painting in pictures_lists:
        (path, distance) = dijkstra(d_map, location, painting, [], {}, {})
        if shortest_distance > distance:
            shortest_distance = distance
            short_path = path
            closed_painting = path[-1]
    return closed_painting, short_path


def get_art_pieces_from_app():
    pictures = server.get_pictures_to_go()
    print(pictures)
    pictures_to_go = []
    for index in range(len(pictures)):
        if pictures[index] == "T":
            pictures_to_go.append(str(index))
    print(pictures_to_go)
    return pictures_to_go


def align_left():
    global robot_orientation
    if robot_orientation == 'N':
        robot_orientation = 'W'
    elif robot_orientation == 'W':
        robot_orientation = 'S'
    elif robot_orientation == 'S':
        robot_orientation = 'E'
    else:
        robot_orientation = 'N'

    turn_left()


def align_right():
    global robot_orientation
    if robot_orientation == 'N':
        robot_orientation = 'E'
    elif robot_orientation == 'E':
        robot_orientation = 'S'
    elif robot_orientation == 'S':
        robot_orientation = 'W'
    else:
        robot_orientation = 'N'

    turn_right()


def align_orientation(desired_orientation):

    first_char = desired_orientation[0]
    if robot_orientation == first_char:
        print("FORWARD!")
        move_forward(100, 100)
        wait_for_motor()
    elif is_orientation_right(first_char):
        print("Turn right")
        turn_right()
    elif is_orientation_left(first_char):
        print("Turn left")
        turn_left()
    elif is_orientation_back(first_char):
        print("Turn back")
        turn_back()
    else:
        print("Errors on aligning orientation - Robot orientation ", robot_orientation,
              " Desired orientation: ", desired_orientation)
    # Update orientation
    global robot_orientation
    robot_orientation = desired_orientation[-1]

    # if len(desired_orientation) == 2:
    #    # Update in special case
    #    robot_orientation = desired_orientation[1]

    print("Current orientation is "+robot_orientation)


def is_orientation_right(desired_orientation):
    if robot_orientation == "N" and desired_orientation == "E":
        return True
    elif robot_orientation == "E" and desired_orientation == "S":
        return True
    elif robot_orientation == "S" and desired_orientation == "W":
        return True
    elif robot_orientation == "W" and desired_orientation == "N":
        return True
    else:
        return False


def is_orientation_left(desired_orientation):
    if robot_orientation == "N" and desired_orientation == "W":
        return True
    elif robot_orientation == "E" and desired_orientation == "N":
        return True
    elif robot_orientation == "S" and desired_orientation == "E":
        return True
    elif robot_orientation == "W" and desired_orientation == "S":
        return True
    else:
        return False


def is_orientation_back(desired_orientation):
    if robot_orientation == "N" and desired_orientation == "S":
        return True
    elif robot_orientation == "E" and desired_orientation == "W":
        return True
    elif robot_orientation == "S" and desired_orientation == "N":
        return True
    elif robot_orientation == "W" and desired_orientation == "E":
        return True
    else:
        return False


def on_pause_command():
    pass


def on_resume_command():
    pass


def is_lost():
    speak("I am lost, please help.")

# #################### OBSTACLE AVOIDANCE #######################


def get_ready_for_obstacle(direction):  # 90 degree
    print("GET READY FOR OBSTACLE")
    if direction == 'RIGHT':
        turn_right_ninety()

        while is_white_line_detected():
            move_forward(100, 100)

    else:  # All default will go through the Left side. IE
        turn_left_ninety()

        while is_white_line_detected():
            move_forward(100, 100)


def go_around_obstacle(direction, get_back_enabled, location_to_go, next_location_to_go):
    print("GO AROUND OBSTACLE Direction: ", direction)
    set_distance = 11
    set_sharp_distance = 15
    is_sharp_before = False
    is_black_detected = False
    if direction == 'RIGHT':
        while not is_white_line_detected():

            if is_black_line_detected() and not is_black_detected:
                is_black_detected = True
                stop_wheel_motor()
                time.sleep(0.5)
                if is_right_black_line_detected():
                    while not (is_left_black_line_detected() or is_left_white_line_detected()):
                        print("Looking for black or white on left sensor")
                        turn(100, 0, 100)

                elif is_left_black_line_detected():
                    while not (is_right_black_line_detected() or is_right_white_line_detected()):
                        print("Looking for black or white on right sensor")
                        turn(0, 100, 100)

                time.sleep(0.5)

                if ((location_to_go, next_location_to_go) in orientation_map) \
                        and (robot_orientation == orientation_map[(location_to_go, next_location_to_go)][0]):
                    # Go forward, count branch
                    get_back_enabled = True
                    global branch_skip
                    branch_skip = True
                    while is_black_line_detected():
                        move_forward(100, 100)
                else:
                    # Need to turn, follow black line
                    get_back_enabled = False
                    align_left()

                    if is_front_obstacle():
                        server.update_status_true('Obstacle detected')

                    while is_front_obstacle():
                        stop_wheel_motor()

                    server.update_status_false('Obstacle detected')

                    # follow black line then break
                    follow_black_line()
                    break

            if get_sonar_readings_front() < set_distance*10:
                turn_right_ninety()
                is_sharp_before = False
            else:
                left = get_sonar_readings_left()
                # print("Left sensor: ", left)
                if left < set_distance:
                    turn(100, 50, 500)
                    is_sharp_before = False
                elif left > set_distance:
                    if (not is_sharp_before) and left > set_sharp_distance:
                        print("Find a sharp!")
                        turn(100, 100, 1000)
                        is_sharp_before = True
                    else:
                        turn(50, 100, 500)
                else:
                    turn(100, 100, 500)
                    is_sharp_before = False

    else:  # All default will go through the Left side. IE
        while not is_white_line_detected():

            if is_black_line_detected() and not is_black_detected:
                is_black_detected = True
                stop_wheel_motor()
                time.sleep(0.5)
                if is_right_black_line_detected():
                    while not (is_left_black_line_detected() or is_left_white_line_detected()):
                        print("Looking for black or white on left sensor")
                        turn(100, 0, 100)
                elif is_left_black_line_detected():
                    while not (is_right_black_line_detected() or is_right_white_line_detected()):
                        print("Looking for black or white on right sensor")
                        turn(0, 100, 100)

                time.sleep(0.5)

                if ((location_to_go, next_location_to_go) in orientation_map) \
                        and (robot_orientation == orientation_map[(location_to_go, next_location_to_go)][0]):
                    # Go forward, count branch
                    get_back_enabled = True
                    print("count branch")
                    global branch_skip
                    branch_skip = True
                    while is_black_line_detected():
                        move_forward(100, 100)
                else:
                    print("turn")
                    # Need to turn, follow black line
                    get_back_enabled = False
                    align_right()

                    if is_front_obstacle():
                        server.update_status_true('Obstacle detected')

                    while is_front_obstacle():
                        stop_wheel_motor()

                    server.update_status_false('Obstacle detected')

                    # follow black line then break
                    follow_black_line()
                    break

            if get_sonar_readings_front() < set_distance*10:
                turn_left_ninety()
                is_sharp_before = False
            else:
                right = get_sonar_readings_right()
                # print("Right sensor: ", right)
                if right < set_distance:
                    turn(50, 100, 500)
                    is_sharp_before = False
                elif right > set_distance:
                    if (not is_sharp_before) and right > set_sharp_distance:
                        print("Find a sharp!")
                        turn(100, 100, 1000)
                        is_sharp_before = True
                    else:
                        turn(100, 50, 500)
                else:
                    turn(100, 100, 500)
                    is_sharp_before = False

    stop_wheel_motor()
    if get_back_enabled:
        get_back_to_line(direction)


def follow_black_line():
    black_target = 18
    errorSumR = 0
    oldR = colour_sensor_right.value()
    oldL = colour_sensor_left.value()
    while not is_right_white_line_detected():
        # Sleeps if Stop
        while is_stop or is_front_obstacle():
            stop_wheel_motor()

        base_speed = 80
        curr_r = colour_sensor_right.value()
        curr_l = colour_sensor_left.value()
        # print(curr_r)
        difference_r = curr_r - black_target
        global errorSumR
        errorSumR += difference_r
        if abs(errorSumR) > 400:
            errorSumR = 400 * errorSumR / abs(errorSumR)
        d = curr_r - oldR

        base_speed -= abs(errorSumR) * 0.14
        if base_speed < default_speed/2.5:
            base_speed = default_speed/2.5
        motor_left.run_forever(speed_sp=base_speed - difference_r * 6 - errorSumR * 0.05 - d * 9)
        motor_right.run_forever(speed_sp=base_speed + difference_r * 6 + errorSumR * 0.05 + d * 9)
        global oldR
        oldR = curr_r
        global oldL
        oldL = curr_l


def get_back_to_line(turning_direction):
    print("GET BACK TO LINE: "+turning_direction)

    if turning_direction == 'RIGHT':
        if is_right_white_line_detected():
            while not is_left_white_line_detected():
                print("Looking for white on left sensor")
                turn(100, 0, 100)

        elif is_left_white_line_detected():
            while not is_right_white_line_detected():
                print("Looking for white on right sensor")
                turn(0, 100, 100)

        time.sleep(0.5)

        turn_right_degree(65)

        time.sleep(0.5)

    else:
        if is_right_white_line_detected():
            while not is_left_white_line_detected():
                print("Looking for white on left sensor")
                turn(100, 0, 100)

        elif is_left_white_line_detected():
            while not is_right_white_line_detected():
                print("Looking for white on right sensor")
                turn(0, 100, 100)

        time.sleep(0.5)

        turn_left_degree(65)

        time.sleep(0.5)


def wait_for_user_to_get_ready():
    print("Press left for single user and press right for double user...")
    button_ev3 = ev3.Button()

    while True:
        if button_ev3.left:
            print("Waiting for User 1 to complete...")
            server.start_up_single()
            print("User 1 is ready!")
            break
        elif button_ev3.right:
            print("Waiting for User 1 and User 2 to complete...")
            server.start_up_double()
            print("Both users are ready!")
            break


def calculate_paintings_order(picture_to_go):
    print("Calculate paintings order")
    virtual_location = robot_location
    virtual_remaining_pictures_to_go = []

    for i in range(len(picture_to_go)):
        closest_painting, path = get_closest_painting(dijkstra_map, virtual_location, picture_to_go)
        server.http_post(int(closest_painting), str(i))
        picture_to_go.remove(closest_painting)
        virtual_remaining_pictures_to_go.append(closest_painting)
        virtual_location = path[-1]
    return virtual_remaining_pictures_to_go


def go_to_closest_painting(toilet, exits, cancel):

    if toilet:
        print("Go to Toilet")
        position, path = get_closest_painting(dijkstra_map, robot_location, ['12'])
        painting = 'Toilet'
    elif exits:
        print("Go to Exit")
        position, path = get_closest_painting(dijkstra_map, robot_location, ['10'])
        painting = 'Exit'
    elif cancel:
        print("Cancel!")
        position, path = get_closest_painting(dijkstra_map, robot_location, ['10'])
        painting = 'Cancel'
    else:
        print("Remain picture: ", remaining_pictures_to_go)
        painting, path = get_closest_painting(dijkstra_map, robot_location, remaining_pictures_to_go)

    # Sanity check, is robot's location the starting position of the shortest path?
    if path[0] != robot_location:
        print("Robot's location is not the starting position of the shortest path")
        exits()

    print("Going to ", painting)
    server.update_art_piece(painting)  # tell the app the robot is going to this painting

    index = 1
    while index < len(path):
        location = path[index]
        while is_branch_detected(colour_sensor_left.value(), colour_sensor_right.value()):
            move_forward(100, 100)

        print("Going to " + location)
        align_orientation(orientation_map[(robot_location, location)])

        # Follow line until reaching a painting OR a branch
        pre_position = motor_right.position

        while True:
            # Sleeps if Stop
            while is_stop:
                stop_wheel_motor()

            base_speed = default_speed
            # print(default_speed)
            # print("Base speed: ", base_speed)
            curr_r = colour_sensor_right.value()
            curr_l = colour_sensor_left.value()
            difference_l = curr_l - target
            difference_r = curr_r - target
            global errorSumR
            errorSumR += difference_r
            if abs(errorSumR) > 400:
                errorSumR = 400 * errorSumR / abs(errorSumR)
            d = curr_r - oldR

            base_speed -= abs(errorSumR) * 0.14
            if base_speed < default_speed/2:
                base_speed = default_speed/2
            PL = 7
            PR = 7.5
            if(default_speed == 180):
                PL = 1
                PR = 8
            modR = difference_r * PR + errorSumR * 0.05 + d * 7
            modL = difference_r * PL + errorSumR * 0.05 + d * 7
            if (modR > base_speed * 1.1):
                modR = base_speed * 1.1
            if (modL > base_speed * 1.1):
                modL = base_speed * 1.1
            motor_right.run_forever(speed_sp=base_speed - modR)
            motor_left.run_forever(speed_sp=base_speed + modL)
            global oldR
            oldR = curr_r
            global oldL
            oldL = curr_l

            if is_front_obstacle():
                stop_wheel_motor()
                print('Distance: ', motor_right.position - pre_position)
                if (robot_location, location) in obstacle_map and (motor_right.position - pre_position) > 100:
                    next_location = 'None'
                    if index < len(path)-1:
                        next_location = path[index+1]
                    stop_wheel_motor()
                    obstacle_turn = obstacle_map[(robot_location, location)]
                    get_ready_for_obstacle(obstacle_turn)  # step 1

                    global branch_skip
                    branch_skip = False
                    go_around_obstacle(obstacle_turn, get_back_enabled=True,
                                       location_to_go=location, next_location_to_go=next_location)
                    if branch_skip:
                        speak('I have skip a branch!')
                        index = index+1
                        global robot_location
                        robot_location = location
                        # global robot_orientation
                        # orientation = orientation_map[(location, next_location)]
                        # robot_orientation = orientation[-1]
                        break
                else:
                    stop_wheel_motor()
                    server.update_status_true('Obstacle detected')
                    speak("Carson, please remove the obstacle in front of me.")
                    # print("Within inside perimeter, obstacle avoidance mode disabled")

                    while is_front_obstacle():
                        stop_wheel_motor()

                    server.update_status_false('Obstacle detected')

            elif is_branch_detected(curr_l, curr_r):
                stop_wheel_motor()
                print("Find a branch")
                # speak('Branch!')
                global robot_location
                robot_location = location
                print("Current location is ", robot_location)
                index = index + 1

                if is_skip and not cancel:  # Only skip at branch
                    print("User press skip!")
                    index = len(path) + 1
                    if not toilet and not exits:
                        remaining_pictures_to_go.remove(painting)
                    # ########### Mahbub wants #####################
                    remaining_pictures_to_go = calculate_paintings_order(remaining_pictures_to_go)
                    server.update_status_false('Skip')

                if is_toilet and not toilet:
                    print("User press toilet!")
                    index = len(path) + 1
                    server.update_status_false('Toilet')
                    go_to_closest_painting(toilet=True, exits=False, cancel=False)
                    # ########### Mahbub wants #####################
                    remaining_pictures_to_go = calculate_paintings_order(remaining_pictures_to_go)

                if is_exit and not exits and not cancel:
                    print("User press exit!")
                    index = len(path) + 1
                    server.update_status_false('Exit')
                    go_to_closest_painting(toilet=False, exits=True, cancel=False)
                    # ########### Mahbub wants #####################
                    remaining_pictures_to_go = calculate_paintings_order(remaining_pictures_to_go)

                if is_cancel and not cancel:
                    print("User press cancel!")
                    index = len(path) + 1
                    server.update_status_false('Cancel')
                    global remaining_pictures_to_go
                    remaining_pictures_to_go = []
                break

    if index == len(path) and not cancel:
        # speak("This is " + art_pieces_map[painting])
        server.set_stop_true()

        point_to_painting(painting)
        server.update_status_arrived(painting)  # tell the app the robot is arrived to this painting

        server.wait_for_continue()  # check for user ready to go

        server.update_status_false(painting)
        server.set_stop_false()

        turn_back_pointer()  # Continue when the stop command become 'F'

        if not toilet and not exits:
            remaining_pictures_to_go.remove(painting)

############################################################

# ##################### POLLING FROM SERVER ########################


def server_check():
    while True:
        server.update_commands()
        #print('Speed: ', server.check_position('Speed'), " Stop: ", server.check_position('Stop')," Skip: ", server.check_position('Skip'), " Toilet: ", server.check_position('Toilet')," Exit: ", server.check_position('Exit'), " Cancel: ", server.check_position('Cancel'))
        global default_speed
        if server.check_position('Speed') == "3":
            default_speed = 140
        elif server.check_position('Speed') == "2":
            default_speed = 100
        elif server.check_position('Speed') == "1":
            default_speed = 60
        else:
            default_speed = 100

        global is_stop
        if server.check_position('Stop') == "T":
            is_stop = True
        else:
            is_stop = False

        global is_skip
        if server.check_position('Skip') == "T":
            is_skip = True
        else:
            is_skip = False

        global is_toilet
        if server.check_position('Toilet') == "T":
            is_toilet = True
        else:
            is_toilet = False

        global is_exit
        if server.check_position('Exit') == "T":
            is_exit = True
        else:
            is_exit = False

        global is_cancel
        if server.check_position('Cancel') == "T":
            is_cancel = True
        else:
            is_cancel = False

        time.sleep(1)


def sensor_hub_check():
    while True:
        hub.poll()

# #################### MAIN #################################
print("SensorHub have set up.")
# speak("Carson, we love you. Group 18. ")

# ################### SETUP ############################
initialising_map()
print("Map has been initialised. Duh")
server = Server()
server_check_thread = Thread(target=server_check)
server_check_thread.daemon = True
server_check_thread.start()

#sensor_hub_check_thread = Thread(target=sensor_hub_check)
#sensor_hub_check_thread.daemon = True
#sensor_hub_check_thread.start()
###########################################################


# ################ MAIN ##########################

target = 50
errorSumR = 0
oldR = colour_sensor_right.value()
oldL = colour_sensor_left.value()
try:
    pr.enable()
    while True:
        print("\n\n\nWaiting for users...")
        speak("Please select the paintings you want to go to.")
        # wait_for_user_to_get_ready()
        server.start_up_single()
        print("Users are ready!")
        print("Current location is ", robot_location, ", facing ", robot_orientation)
        pictures_to_go = get_art_pieces_from_app()
        # ########### Mahbub wants #####################
        remaining_pictures_to_go = calculate_paintings_order(pictures_to_go)
        ################################################
        print(remaining_pictures_to_go)
        while not len(remaining_pictures_to_go) == 0:
            go_to_closest_painting(toilet=False, exits=False, cancel=False)

        # If no more painting to go, do this
        while not robot_location == '10':
            print("No more pictures to go. Go to exit.")
            go_to_closest_painting(toilet=False, exits=False, cancel=True)   # Go to exit

        align_orientation('N')
        server.update_status_arrived('Exit')
        server.set_stop_true()
        print("Finish program!")
        server.reset_list_on_server()
        # terminate thread stop_thread
        # exit()


except KeyboardInterrupt:
    motor_left.stop()
    motor_right.stop()
    pr.disable()
    pr.dump_stats("profiled.log")
    pr.print_stats('cumtime')
    raise

