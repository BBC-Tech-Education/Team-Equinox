from hub import port, motion_sensor, button
import motor
import color_sensor
import distance_sensor
import math
import time
motion_sensor.reset_yaw

# Asign ports to different quadrents
FR = port.D
BR = port.C
BL = port.B
FL = port.A
MAX_ACCELERATION = 5000
MAX_SPEED = 1400
ROTATION_MULTI = -25.0
MAX_STRENGTH = 55




#Different forms of movement 

def orbit():
    global FR_SPEED, BR_SPEED, BL_SPEED, FL_SPEED
    FR_SPEED = int(math.cos(math.radians(offset)) * speed - math.sin(math.radians(offset)) * speed + rotation)
    BR_SPEED = int(math.cos(math.radians(offset)) * speed + math.sin(math.radians(offset)) * speed + rotation)
    BL_SPEED = int(math.cos(math.radians(offset)) * speed - math.sin(math.radians(offset)) * speed - rotation)
    FL_SPEED = int(math.cos(math.radians(offset)) * speed + math.sin(math.radians(offset)) * speed - rotation)
def move_forward_defence():
    global FR_SPEED, FL_SPEED, BL_SPEED, BR_SPEED
    FR_SPEED = int(math.cos(math.radians(ball_degree)) * speed - math.sin(math.radians(ball_degree)) * speed + rotation)
    BR_SPEED = int(math.cos(math.radians(ball_degree)) * speed + math.sin(math.radians(ball_degree)) * speed + rotation)
    BL_SPEED = int(math.cos(math.radians(ball_degree)) * speed - math.sin(math.radians(ball_degree)) * speed - rotation)
    FL_SPEED = int(math.cos(math.radians(ball_degree)) * speed + math.sin(math.radians(ball_degree)) * speed - rotation)
def move_back_defence():
    global FR_SPEED, FL_SPEED, BL_SPEED, BR_SPEED
    FR_SPEED = int(math.cos(math.radians(f)) * speed - math.sin(math.radians(f)) * speed + rotation)
    BR_SPEED = int(math.cos(math.radians(f)) * speed + math.sin(math.radians(f)) * speed + rotation)
    BL_SPEED = int(math.cos(math.radians(f)) * speed - math.sin(math.radians(f)) * speed - rotation)
    FL_SPEED = int(math.cos(math.radians(f)) * speed + math.sin(math.radians(f)) * speed - rotation)
def move_right_defence():
    global FR_SPEED, FL_SPEED, BL_SPEED, BR_SPEED
    FR_SPEED = int(math.cos(math.radians(90)) * speed - math.sin(math.radians(90)) * speed + rotation)
    BR_SPEED = int(math.cos(math.radians(90)) * speed + math.sin(math.radians(90)) * speed + rotation)
    BL_SPEED = int(math.cos(math.radians(90)) * speed - math.sin(math.radians(90)) * speed - rotation)
    FL_SPEED = int(math.cos(math.radians(90)) * speed + math.sin(math.radians(90)) * speed - rotation)
def move_left_defence():
    global FR_SPEED, FL_SPEED, BL_SPEED, BR_SPEED
    FR_SPEED = int(math.cos(math.radians(-90)) * speed - math.sin(math.radians(-90)) * speed + rotation)
    BR_SPEED = int(math.cos(math.radians(-90)) * speed + math.sin(math.radians(-90)) * speed + rotation)
    BL_SPEED = int(math.cos(math.radians(-90)) * speed - math.sin(math.radians(-90)) * speed - rotation)
    FL_SPEED = int(math.cos(math.radians(-90)) * speed + math.sin(math.radians(-90)) * speed - rotation)
def not_moving():
    global FR_SPEED, FL_SPEED, BL_SPEED, BR_SPEED
    FR_SPEED = 0+rotation
    BL_SPEED = 0-rotation
    BR_SPEED = 0+rotation
    FL_SPEED = 0-rotation
# Movement set up
def run_motors():
    motor.run(FR, int(FR_SPEED), acceleration=MAX_ACCELERATION)
    motor.run(FL, int(-FL_SPEED), acceleration=MAX_ACCELERATION)
    motor.run(BR, int(BR_SPEED), acceleration=MAX_ACCELERATION)
    motor.run(BL, int(-BL_SPEED), acceleration=MAX_ACCELERATION)

# def constrain(val, min_val, max_val):
#     if val < min_val:
#         return min_val
#     if val > max_val:
#         return max_val
#     return val

while True:
        # Changing variables
    
    
    motion_sensor.reset_yaw
    # Set constants
    FR_SPEED = 0
    BL_SPEED = 0
    BR_SPEED = 0
    FL_SPEED = 0
    offset = 0
    data = color_sensor.rgbi(port.F)
    ball_strength = data[1]
    ball_direction = data[0]
    decimal_ball_strength = ball_strength / MAX_STRENGTH
    back_half_additinal = 0
    ball_degree = data[2]
    #getting yaw and applying adjustment
    bearing = motion_sensor.tilt_angles()[0] / 10
    ultra_sonic_distance = distance_sensor.distance(port.E)

    speed = 1000
    # if button.RIGHT:
    #     speed = 1200
    rotation = bearing * ROTATION_MULTI


    # creating offset
    def angle_zero(angle):
        if(angle <= 180):
            return angle
        elif(angle > 180):
            return angle - 360
        else:
            return 0
    angle = angle_zero(ball_degree)# Angles is 180 -180
    y_offset = int(min(0.04 * math.e ** (0.157 * abs(angle)), 90))
    x_scaling = int(min(0.02 * math.e ** (10 * ball_strength), 1))#
    if ball_degree<= 180:
        offset = ball_degree + (y_offset * x_scaling)
    else:
        offset = ball_degree - (y_offset * x_scaling)
    # insuring that ball_degree is 180 to -180
    if ball_degree > 180:
        ball_degree = ball_degree - 360



                                    

# making sure -180 < offset < 180
    if offset > 180:
        offset = offset - 360
    if offset < -180:
        offset = offset + 360
    # Getting a movement angle for when ultra sonic > 40cm / 400mm
    defence_multi = (-0.0111111 * abs(ball_degree) + 1)
    added_defence_angle = 180 * defence_multi    
    f = (abs(ball_degree) + added_defence_angle)
    if ball_degree < 0:
        f = f * -1
    # defensive requirments for different forms of movement. As well as some changed variables based on positioning
    if ball_direction == 0:
        speed = 600
        if ultra_sonic_distance > 600 or ultra_sonic_distance == -1:
            speed = max(ultra_sonic_distance * 1.5, 300)
            move_back_defence()
        elif ultra_sonic_distance < 500:
            orbit()
        else:
            not_moving()
    elif ball_degree > 90 or ball_degree < -90:
        orbit()
        
    # elif ball_degree == 0  and ball_strength >= 40:
    #     speed = 900
    #     orbit()
    elif ball_strength >= 40 and (ball_degree < 3 or ball_degree > -3) and ball_direction == 1:
        speed = 1000
        orbit()
        if ultra_sonic_distance > 800 and (ball_degree < 3 or ball_degree > -3):
            not_moving()
    # elif ball_strength > 45:
    #     orbit()
    #     if ultra_sonic_distance > 700 and (ball_degree < 10 or ball_degree > -10):
    #         not_moving()
    
        # if ultra_sonic_distance > 700 and (ball_degree < 10 or ball_degree > 350):
        #    not_moving()
    

        
    elif 500 < ultra_sonic_distance < 600:
        if ball_degree > 0:
            speed = 3.5 * abs(-0.00122751 * (abs(ball_degree)** 4) + 0.106984 * (abs(ball_degree)** 3) - 2.85026 * (abs(ball_degree) ** 2) + 39.03175 * abs(ball_degree))#min(800, abs(ball_degree * 35))
            move_right_defence()
        elif ball_degree < 0:
            speed = 3.5 * abs(-0.00122751 * (abs(ball_degree)** 4) + 0.106984 * (abs(ball_degree)** 3) - 2.85026 * (abs(ball_degree) ** 2) + 39.03175 * abs(ball_degree))#min(800, abs(ball_degree * 35))
            move_left_defence()
        else:
            not_moving()
    elif ultra_sonic_distance < 500:
        speed = min(500, abs(ball_degree * 30))
        orbit()
    elif ultra_sonic_distance > 600 or ultra_sonic_distance == -1:
        speed = max(ultra_sonic_distance * 1.5, 300)
        move_back_defence()
    else:
        not_moving()

   # Scaling motor speeds incase the speed is greater than what the motors max speed is.
   
    # Flipping two motors to negative 

    # Running the motors
    # run_motors()
    
    

    print(ball_degree, ball_strength)
    run_motors()
    