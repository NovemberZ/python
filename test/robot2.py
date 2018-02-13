#!/usr/bin/env python
# coding: utf-8

import requests
import time
import numpy as np

base_url = 'http://47.94.14.199:7777/robot'
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsiYXBpIl0sInV1aWQiOiI0ZDg4NmY0NjU3M2I0Yjg4' \
        'YmE1YWQ5MDBkYjcwMzUzOSJ9.yShj0DZpbJCIuYW3VPg9WzRWCbtt_q6SRKSivcVLDEY'

Frequency = 2  # 目前的频率


def get_robots():
    r = requests.get(base_url, params={'token': token})
    resp = r.json()  # have already trans to dict # actually a decoder to dict
    print(resp["connected_robots"])
    return resp["connected_robots"]


def robot_status(robot_name):
    url_ = base_url + '/{}/robot_status'.format(robot_name)
    r = requests.get(url_, params={'token': token})
    rsp = r.json()
    return rsp


def get_markers(robot_name):
    url_ = base_url + '/{}/markers'.format(robot_name)
    params_ = {'token': token}  # use key to set the marker type, default is 0
    r = requests.get(url_, params=params_)
    rsp = r.json()
    return rsp


def robot_action(robot_name, lv, av):
    url_ = base_url + '/{}/joystick'.format(robot_name)
    while 1:
        r = requests.get(url_, params={'linear_velocity': lv, 'angular_velocity': av, 'token': token})
        rsp = r.json()
        if rsp["status"] == 'OK':  # 避免多个指令同时进行造成 混乱
            break
        else:
            time.sleep(0.1)


def get_robot_position(robot_name):
    st = robot_status(robot_name)
    return st['results']['current_pose']


def get_marker_position(robot_name, marker_name):
    st = get_markers(robot_name)
    return st['results'][marker_name]['pose']['position']


# 修改了get_yaw相关的一些可能存在的隐患
def get_yaw(ore):  # 根据{x,y,z,w}计算点的方位：目前用在计算marker的方向
    pi = 3.1416  # very important; 应该设置比实际的pi值大一点
    yaw = 2 * np.arctan2(ore[0], ore[1])
    if pi < yaw <= 2 * pi:
        yaw -= 2 * pi
    if -pi > yaw >= -2 * pi:
        yaw += 2 * pi
    return yaw


def turn_to_0_360(rad):
    rad = (2*np.pi + rad) if rad < 0 else rad
    rad = (rad - 2*np.pi) if rad >= 2*np.pi else rad
    return rad

# 把反向向量调成正向；
def turn_180(angle, angle_cos):
    # 对到marker的向量做反向调整
    angle = angle - np.pi if angle_cos < 0 else angle
    return angle

# 调整角度为锐角
def turn_1_4_quadrant(angle):
    # 调整角度为锐角
    angle = angle - 2 * np.pi if angle > np.pi else angle
    angle = angle + 2 * np.pi if angle < -np.pi else angle
    return angle


def diff_distance(robot_name, mk_name):  # 计算两个点的距离差
    markers_info = get_markers(robot_name)

    st = robot_status(robot_name)
    cur_pos = st['results']["current_pose"]
    cur_pos = list(cur_pos.values())
    tar_pos = markers_info['results'][mk_name]['pose']['position']
    tar_pos = list(tar_pos.values())

    diff_pos = np.array(tar_pos[:2]) - np.array(cur_pos[:2])
    distance = np.linalg.norm(diff_pos)
    return distance


def get_robot_to_marker_vector(robot_name, marker_name):
    mk_pos = get_marker_position(robot_name, marker_name)
    rb_pos = get_robot_position(robot_name)
    return np.array([(mk_pos['x'] - rb_pos['x']), (mk_pos['y'] - rb_pos['y'])])


def get_robot_theta(robot_name):
    theta = robot_status(robot_name)['results']['current_pose']['theta']
    return theta


def get_unit_vector(angle):
    vec_y = np.sin(angle)
    vec_x = np.cos(angle)
    return np.array([vec_x, vec_y])


def cos_np(robot_name, marker_name):
    mv_vec = get_robot_to_marker_vector(robot_name, marker_name)
    rb_theta = get_robot_theta(robot_name)
    rb_vec = get_unit_vector(rb_theta)
    return np.dot(mv_vec, rb_vec) / (np.linalg.norm(mv_vec) * (np.linalg.norm(rb_vec)))


def diff_angle_with_move(robot_name, marker_name):
    mv_vec = get_robot_to_marker_vector(robot_name, marker_name)
    mv_theta = np.arctan2(mv_vec[1], mv_vec[0])
    rb_theta = get_robot_theta(robot_name)
    mv_theta_p = turn_to_0_360(mv_theta)
    rb_theta_p = turn_to_0_360(rb_theta)
    minus_rad = mv_theta_p - rb_theta_p
    minus_rad = minus_rad - 2 * np.pi if minus_rad > np.pi else minus_rad
    minus_rad = minus_rad + 2 * np.pi if minus_rad < -np.pi else minus_rad
    return minus_rad

#
# def minus_rad(robot_name, mk_name):  # 计算两个点的方位差
#     markers_info = get_markers(robot_name)
#     mk_orient = markers_info['results'][mk_name]['pose']["orientation"]
#     tar_rad = get_yaw(list((mk_orient['z'], mk_orient['w'])))
#     st = robot_status(robot_name)
#     cur_rad = st['results']["current_pose"]["theta"]
#     diff_rad = cur_rad - tar_rad
#     return diff_rad

def diff_angle_with_marker(robot_name, marker_name):
    rb_theta = get_robot_theta(robot_name)
    markers_info = get_markers(robot_name)
    mk_orient = markers_info['results'][marker_name]['pose']["orientation"]
    marker_rad = get_yaw(list((mk_orient['z'], mk_orient['w'])))

    minus_rad = marker_rad - rb_theta
    minus_rad = minus_rad - 2 * np.pi if minus_rad > np.pi else minus_rad
    minus_rad = minus_rad + 2 * np.pi if minus_rad < -np.pi else minus_rad
    return minus_rad

# 调整机器人行走时方向
def adjust_robot_move_direction(robot_name, marker_name):
    print('移动时的角度调整开始...')
    cos_mtr = cos_np(robot_name, marker_name)
    print('与目标方向呈:', ('锐角' if cos_mtr > 0 else '钝角'))
    angle = diff_angle_with_move(robot_name, marker_name)
    print('初始夹角1:', angle, 'rad')
    angle = turn_180(angle, cos_mtr)
    print('初始夹角2:', angle, 'rad')
    angle = turn_1_4_quadrant(angle)
    print('初始夹角3:', angle, 'rad')

    while np.abs(angle) > MOVE_MIN_RAD: # 注意这是个超参数：当小余这个角度时，停止调节
        print('开始调整:', ('左转' if angle > 0 else '右转'))
        robot_action(robot_name, 0, angle)
        angle = diff_angle_with_move(robot_name, marker_name)
        print('调整后的角度1:', angle, 'rad')
        angle = turn_180(angle, cos_mtr)
        print('调整后的角度2:', angle, 'rad')
        angle = turn_1_4_quadrant(angle)
        print('调整后的角度3:', angle, 'rad')
        # time.sleep(1/Frequency - 0.1)

# 调整机器人停止时方向
def adjust_robot_stop_direction(robot_name, marker_name):
    print('停止后的角度调整开始...')
    angle = diff_angle_with_marker(robot_name, marker_name)
    print('初始夹角1:', angle, 'rad')
    angle = turn_1_4_quadrant(angle)
    print('初始夹角2:', angle, 'rad')

    while np.abs(angle) > STOP_MIN_RAD: # 注意这是个超参数：当小余这个角度时，停止调节
        print('开始调整:', ('左转' if angle > 0 else '右转'))
        robot_action(robot_name, 0, angle)
        time.sleep(1)
        angle = diff_angle_with_marker(robot_name, marker_name)
        # 调整角度为锐角
        print('调整后的夹角1:', angle, 'rad')
        angle = turn_1_4_quadrant(angle)
        print('调整后的夹角2:', angle, 'rad')


# 调整机器人位置
def adjust_robot_location(robot_name, marker_name):
    print('位置调整开始...')
    distance = diff_distance(robot_name, marker_name)
    print('初始距离:', distance, 'm')

    i = 0
    while distance > STOP_MIN_DIS:
        if i > MOVE_MAX_STEP:
            break
        # 每次调整位置前都先调整方向，防止由于位置的改变导致方向差距变大
        adjust_robot_move_direction(robot_name, marker_name)

        cos_mtr = cos_np(robot_name, marker_name)
        print('角度调整后的cos:', cos_mtr)
        # 调整位置
        if cos_mtr >= 0:
            robot_action(robot_name, distance, 0)  # 前进
            print('与目标方向呈锐角，前进.')
        else:
            robot_action(robot_name, -distance, 0)  # 后退
            print('与目标方向呈钝角，后退.')
        distance = diff_distance(robot_name, marker_name)
        print('调整后的距离:', distance, 'm')
        i = i + 1


# def robot_move(robot_name, marker_name):

#     # 调整方向
#     adjust_robot_direction(robot_name, marker_name, min_rad)
#     # 调整位置
#     adjust_robot_location(robot_name, marker_name, min_length)
#
#     print '最终与目标角度 [%s]rad.' % check_dir(robot_name, marker_name)
#     print '最终与目标距离 [%s]m.' % check_ln_dir(robot_name, marker_name)


def grad_adjust_robot(robot_name, marker_name):
    # 1. 运动时调整位置
    adjust_robot_location(robot_name, marker_name)
    # 2. 停止后调整角度
    adjust_robot_stop_direction(robot_name, marker_name)


# move_to_marker('robot_arm_test', 'test2')
def move_to_marker(robot_name, marker_name):
    print('开始移动到marker...')
    url_ = base_url + '/{}/move'.format(robot_name)
    params_ = {'marker': marker_name, 'token': token}
    requests.get(url_, params=params_)

    while 1:
        st = robot_status(robot_name)
        move_status = st['results']['move_status']
        move_target = st['results']['move_target']
        if move_status == 'succeeded' and move_target == marker_name:
            break
        else:
            time.sleep(0.1)

    print('移动到marker:', marker_name)


# move_to_marker('robot_arm_test', 'test2')
def move_tune_to_marker(robot_name, marker_name):
    move_to_marker(robot_name, marker_name)

    print('微调开始...')
    start = time.time()
    grad_adjust_robot(robot_name, marker_name)

    print('微调完成-------------------------------------')
    print('标注点:', marker_name)
    print('位置差:', diff_distance(robot_name, marker_name))
    print('角度差:', diff_angle_with_marker(robot_name, marker_name))
    print('耗时  :', time.time() - start, 's')


MOVE_MAX_STEP = 10 # 移动的最大步数
MOVE_MIN_RAD = 0.3 # 弧度
STOP_MIN_RAD = 0.05 # 弧度
STOP_MIN_DIS = 0.05 # 米

def move_to_test1():
    move_tune_to_marker('robot_arm_test', 'test1')

def move_to_test2():
    move_tune_to_marker('robot_arm_test', 'test2')

def move_to_test5():
    move_tune_to_marker('robot_arm_test', 'test5')

def move_to_test6():
    move_tune_to_marker('robot_arm_test', 'test6')

def move_to_test7():
    move_tune_to_marker('robot_arm_test', 'test7')