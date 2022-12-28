import cv2 
import numpy as np 
import matplotlib.pyplot as plt
import sys
import math
import io
import pyqrcode
import base64

def canny_edge_detector(image): 
      
    # Convert the image color to hsv 
    hsv_img = cv2.cvtColor(image, cv2.COLOR_RGB2HSV) 
    # hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
    # hsv_img = image
    # cv2.imshow("results", hsv_img)
    # cv2.waitKey(0)
    # Convert the image to grayscale afters selecting the tracks color
    lower_blue = np.array([0, 100, 40])
    upper_blue = np.array([80, 255, 255])
    # gray = cv2.inRange(hsv_img, lower_white, upper_white)
    # lower_blue = np.array([5, 60, 120])
    # upper_blue = np.array([190, 255, 255])

    gray = cv2.inRange(hsv_img, lower_blue, upper_blue)
    # gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # cv2.imshow("results", gray)
    # cv2.waitKey(0)
    # Reduce noise from the image 
        # blur = cv2.GaussianBlur(gray, (5, 5), 0) 
        # cv2.imshow("results", blur)
        # cv2.waitKey(0) 
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    # canny = cv2.Canny(gray, 200, 400)
    canny = cv2.Canny(gray, 50, 150)
    # cv2.imshow("results", canny)
    # cv2.waitKey(0) 
    return canny

def region_of_interest(image): 
    height, width = image.shape
    polygon = np.array([[
        (0, height * 1 / 4),
        (width, height * 1 / 4),
        (width, height),
        (0, height),
    ]], np.int32)
    # polygon = np.array([[
    #     (0, 0),
    #     (width, 0),
    #     (width, height),
    #     (0, height),
    # ]], np.int32)
    # polygon = np.array([[
    #     (0, 0),
    #     (width, 0),
    #     (width, 3/4*height),
    #     (0, 3/4*height),
    # ]], np.int32)
    

    mask = np.zeros_like(image) 
    # Fill poly-function deals with multiple polygon 
    cv2.fillPoly(mask, polygon, 255)  
      
    # Bitwise operation between canny image and mask image 
    masked_image = cv2.bitwise_and(image, mask)
    # cv2.imshow("results", masked_image)
    # cv2.waitKey(0) 
    return masked_image 

def detect_line_segments(cropped_edges):
    # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
    rho = 1  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 10  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, 
                                    np.array([]), minLineLength=10, maxLineGap=4)
    # print(line_segments)
    return line_segments

def make_points(frame, line):
    height, width, _ = frame.shape
    slope, intercept = line
    y1 = height  # bottom of the frame
    y2 = 0#int(y1 * 1 / 2)  # make points from middle of the frame down

    # bound the coordinates within the frame
    x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
    x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
    return [[x1, y1, x2, y2]]

def average_slope_intercept(frame, line_segments):
    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
    """
    lane_lines = []
    if line_segments is None:
        # logging.info('No line_segment segments detected')
        return lane_lines

    height, width, _ = frame.shape
    left_fit = []
    right_fit = []

    boundary = 1/3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

    for line_segment in line_segments:
        for x1, y1, x2, y2 in line_segment:
            if x1 == x2:
                # logging.info('skipping vertical line segment (slope=inf): %s' % line_segment)
                continue
            fit = np.polyfit((x1, x2), (y1, y2), 1)
            slope = fit[0]
            intercept = fit[1]
            if slope < 0:
                if x1 < left_region_boundary and x2 < left_region_boundary:
                    left_fit.append((slope, intercept))
            else:
                if x1 > right_region_boundary and x2 > right_region_boundary:
                    right_fit.append((slope, intercept))

    left_fit_average = np.average(left_fit, axis=0)
    if len(left_fit) > 0:
        lane_lines.append(make_points(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(make_points(frame, right_fit_average))

    # logging.debug('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

    return lane_lines


def display_lines(frame, lines, line_color=(0, 255, 0), line_width=2):
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image

def compute_steering_angle(frame, lane_lines):
    height, width, _ = frame.shape
    if len(lane_lines) == 1:
        # logging.debug('Only detected one lane line, just follow it. %s' % lane_lines[0])
        # print("lines are one")
        x1, _, x2, _ = lane_lines[0][0]
        # x_offset = x1
        x_offset = (-x1 + x2)
        y_offset = int(height/2)
    elif len(lane_lines) < 1:
        return -270
    else:
        # print("lines are more than one")
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        camera_mid_offset_percent = 0.0 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
        mid = int(width / 2 * (1 + camera_mid_offset_percent))
        x_offset = (left_x2 + right_x2) / 2 - mid
        y_offset = int(height/2)

    angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
    angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
    steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

    # logging.debug('new steering angle: %s' % steering_angle)
    return steering_angle

def display_heading_line(frame, steering_angle, line_color=(0, 0, 255), line_width=5 ):
    heading_image = np.zeros_like(frame)
    height, width, _ = frame.shape
 
    steering_angle_radian = steering_angle / 180.0 * math.pi
    x1 = int(width / 2)
    y1 = height
    x2 = int(x1 - height / 2 / math.tan(steering_angle_radian))
    y2 = 0#int(height / 2)
    cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
    heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

    return heading_image




# def main_prog(image):
#     # im = np.frombuffer(base64.b64decode(image), np.uint8)
#     im = np.frombuffer(base64.b64decode(image), np.uint8)
#     frame = cv2.imdecode(im, cv2.IMREAD_COLOR)
#     # frame = cv2.imread("blue123.jpg")
#     canny_image = canny_edge_detector(frame) 
#     cropped_edges = region_of_interest(canny_image) 
#     line_segments = detect_line_segments(cropped_edges)
#     lane_lines = average_slope_intercept(frame, line_segments)
#     lane_lines_image = display_lines(frame, lane_lines)
#     # cv2.imshow("results", lane_lines_image)
#     # cv2.waitKey(0)
#     steering_ang = compute_steering_angle(frame, lane_lines)
#     decision_img = display_heading_line(lane_lines_image, steering_ang)
#     # decision_img = display_heading_line(lane_lines_image, 135)
#     # cv2.imshow("results", decision_img)
#     # cv2.waitKey(1500)
#     cv2.imwrite('uploads/lena_opencv_red.jpg', decision_img)
#     # print(steering_ang)
#     if(steering_ang > 108):
#         return "Right"
#     elif(steering_ang < 72 and steering_ang > 0):
#         return "Left"
#     elif(steering_ang >72 and steering_ang < 108):
#         return "Forward"
#     else:
#         return "Forward"


# im = np.frombuffer(base64.b64decode(image), np.uint8)
#image = open(sys.argv[1], 'r').read()
# image = open("uploads/20photo.txt",'r').read()
#image = bytes(image, 'utf-8')
#im = np.frombuffer(base64.b64decode(image), np.uint8)
#frame = cv2.imdecode(im, cv2.IMREAD_COLOR)
frame = cv2.imread(sys.argv[1])
canny_image = canny_edge_detector(frame) 
cropped_edges = region_of_interest(canny_image) 
line_segments = detect_line_segments(cropped_edges)
lane_lines = average_slope_intercept(frame, line_segments)
lane_lines_image = display_lines(frame, lane_lines)
# cv2.imshow("results", lane_lines_image)
# cv2.waitKey(0)
steering_ang = compute_steering_angle(frame, lane_lines)
decision_img = display_heading_line(lane_lines_image, steering_ang)
# decision_img = display_heading_line(lane_lines_image, 135)
#cv2.imshow("results", decision_img)
# cv2.waitKey(500)
cv2.imwrite('uploads/album.jpg', decision_img)
#print( "steering_ang: "+steering_ang)
if(steering_ang > 112):
    #Right
    print(2) 
elif(steering_ang < 72 and steering_ang > 0):
    #Left
    print(3)
elif(steering_ang >72 and steering_ang < 108):
    #Forward
    print(1)
else:
    print(1)
# print("\nthe steering angle: ", steering_ang)
