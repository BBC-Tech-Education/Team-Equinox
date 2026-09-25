from hub import port, motion_sensor, button
import motor
import color_sensor
import distance_sensor
import math
import time
motion_sensor.reset_yaw


#################### CONSTANTS ####################

# Motors
FR = port.D
FL = port.A
BL = port.B
BR = port.C

MAX_ACCELERATION = 5000
MAX_SPEED = 1400
MOVE_SPEED = 1500
ROTATION_MULTI = -17.0

MOTOR_UPDATE_PERIOD = 20

# IR Ring
IR_UPDATE_PERIOD = 20
IR_PORT = port.F

IR_ANGLE_SIMPE = 0
IR_STRENGTH = 1
IR_ANGLE = 2

# Ultrasonic
US_PORT = port.E
US_UPDATE_PERIOD = 50

WALL_DIST_DODGY_RANGE = 75
WALL_DIST_GOOD_RANGE = 200
WALL_DIST_VAL_CHANGE = 30
WALL_DIST_MULTI = 0.6875

INTERCEPT_VAL_CHANGE = 40
INTERCEPT_DODGY_RANGE = 150

FIELD_WIDTH = 160
MAX_TARGET_CHANGE = 30



# IMU
IMU_UPDATE_PERIOD = 5




#################### GLOBAL VARIABLES ####################

# Ir Ring
ir_data = 0

# Ultrasonic
us_dist = 0
last_us_dist = 0

intercept_robot = False

wall_dist = 0
last_wall_dist = 0

# IMU
target = 0
bearing = 0

# Update Timers

last_ultrasonic = time.ticks_ms()
last_ir         = time.ticks_ms()
last_motors     = time.ticks_ms()
last_imu        = time.ticks_ms()
update_us       = 0


#################### FUNCTIONS ####################


def run_motors(direction: int, speed: int, rotation: int):
    motor.run(FR, int(math.cos(math.radians(direction + 45))  * speed + rotation), acceleration=MAX_ACCELERATION)
    motor.run(BR, int(math.cos(math.radians(direction - 45))  * speed + rotation), acceleration=MAX_ACCELERATION)
    motor.run(BL, int(math.cos(math.radians(direction - 135)) * speed + rotation), acceleration=MAX_ACCELERATION)
    motor.run(FL, int(math.cos(math.radians(direction + 135)) * speed + rotation), acceleration=MAX_ACCELERATION)



################### INTIAL VALUES ###################

ir_data = color_sensor.rgbi(IR_PORT)
bearing = motion_sensor.tilt_angles()[0] / 10
last_wall_dist = abs((distance_sensor.distance(US_PORT) / 10) * math.cos(math.radians(bearing)))
last_us_dist = distance_sensor.distance(US_PORT) / 10

#################### LOOP ####################

while True:
    
    current_time = time.ticks_ms()

    if time.ticks_diff(current_time, last_ir) >= IR_UPDATE_PERIOD:
        ir_data = color_sensor.rgbi(IR_PORT)
        last_ir = time.ticks_ms()

    if time.ticks_diff(current_time, last_ultrasonic) >= US_UPDATE_PERIOD:
        intercept_robot = False
        us_dist = distance_sensor.distance(US_PORT) / 10


        if abs(last_us_dist - us_dist > INTERCEPT_VAL_CHANGE):
            us_dist = FIELD_WIDTH / 2
            intercept_robot = True


        wall_dist = abs(us_dist * math.cos(math.radians(bearing)))


        print("CURRENT: us - ", us_dist, " wall - ", wall_dist, end="")
        ##### Dealing with bad ulstrasonic values #####
        if intercept_robot == False:
            if last_wall_dist < WALL_DIST_DODGY_RANGE:
                if wall_dist < WALL_DIST_GOOD_RANGE:
                    if abs(wall_dist - last_wall_dist) > WALL_DIST_VAL_CHANGE:
                        wall_dist = last_wall_dist
                
        print("\tADJUSTED: wall - ", wall_dist, intercept_robot)
        

        # intercept_robot = 0
        # new_ultrasonic = distance_sensor.distance(US_PORT) / 10
        # if new_ultrasonic < 0:
        #     new_ultrasonic = ultrasonic_distance
        # if new_ultrasonic > ultrasonic_distance + 40:
        #     new_ultrasonic = ultrasonic_distance
        #     intercept_robot = 1
        # if new_ultrasonic < ultrasonic_distance - 40:
        #     new_ultrasonic = ultrasonic_distance
        #     intercept_robot = 1
        # print(intercept_robot, ultrasonic_distance, distance_sensor.distance(US_PORT) / 10)
        
        # ultrasonic_distance = new_ultrasonic
        last_us_dist = us_dist
        last_wall_dist = wall_dist
        last_ultrasonic = time.ticks_ms()

    if time.ticks_diff(current_time, last_imu) >= IMU_UPDATE_PERIOD:
        bearing = motion_sensor.tilt_angles()[0] / 10
        last_imu = time.ticks_ms()

    
    if time.ticks_diff(current_time, last_motors) >= MOTOR_UPDATE_PERIOD:
        # INSERT GOAL CORRECT CODE HERE
        # if GOAL CORRECT:
        #    put code in here to change the target to face the goal
        # else:
        #target = 0
        
        if wall_dist >= FIELD_WIDTH:
            wall_dist = FIELD_WIDTH

        # print("Wall Distance: ", wall_distance)
        target = int(0.6875 * (wall_dist - (FIELD_WIDTH / 2)))

        if target < -MAX_TARGET_CHANGE:
            target = -MAX_TARGET_CHANGE
        elif target > MAX_TARGET_CHANGE:
            target = MAX_TARGET_CHANGE


        
        rotation = bearing + target

        if rotation <= -180:
            rotation += 360
        elif rotation > 180:
            rotation -= 360

        rotation = int(rotation * ROTATION_MULTI);


        ball_angle = ir_data[IR_ANGLE]
        if ball_angle > 180:
            ball_angle -= 360
        
        y_offset = int(min(0.04 * math.exp(0.16 * abs(ball_angle)), 80))
        x_scaling = int(min(0.02 * math.exp(10 * (ir_data[IR_STRENGTH] / 100)), 1))#int(min(0.02 * math.exp(4.5 * ball_strength)), 1))

        move_angle = 0
        if ball_angle < 0:
            move_angle = ball_angle - (y_offset * x_scaling)
        else:
            move_angle = ball_angle + (y_offset * x_scaling)

        if move_angle > 180:
            move_angle -= 360
        if move_angle < -180:
            move_angle += 360

        
        if button.pressed(button.RIGHT):
            move_speed = 0
        else:
            if not ir_data[IR_STRENGTH] == 0:
                move_speed = MOVE_SPEED
            else:
                move_speed = 0
        
        
        run_motors(move_angle, move_speed, rotation)
        last_motors = time.ticks_ms()