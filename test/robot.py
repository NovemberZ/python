import requests
import time
import numpy as np
import pandas as pd

base_url = 'http://47.94.14.199:7777/robot'
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZXMiOlsiYXBpIl0sInV1aWQiOiI0ZDg4NmY0NjU3M2I0Yjg4YmE1YW' \
        'Q5MDBkYjcwMzUzOSJ9.yShj0DZpbJCIuYW3VPg9WzRWCbtt_q6SRKSivcVLDEY'
pi = 3.1416
Frequency = 2  # 目前的频率


def available_robot():
    r = requests.get(base_url, params={'token': token})
    resp = r.json()  # have already trans to dict # actually a decoder to dict
    print(resp["connected_robots"])
    return resp["connected_robots"]


def move_to_marker(robot_name, marker_name):
    url_ = base_url + '/{}/move'.format(robot_name)
    params_ = {'marker': marker_name, 'token': token}
    r = requests.get(url_, params=params_)


def marker_error(robot_name, marker_name):
    st = status(robot_name)
    cur_pos = st['results']["current_pose"]
    cur_pos = np.array(list(cur_pos.values()))[:2]
    move_status = st['results']['move_status']
    move_target = st['results']['move_target']
    print(move_status, move_target)
    marks_info = get_markers(robot_name)
    tar_pos = marks_info['results'][marker_name]['pose']['position']
    tar_pos = np.array(list(tar_pos.values()))[:2]
    err = np.linalg.norm(cur_pos - tar_pos)
    return err


def put_marker(robot_name, marker_name):
    url_ = base_url + '/{}/markers'.format(robot_name)
    params_ = {'name': marker_name, 'marker_type': '0'}  # use key to set the marker type, default is 0
    r = requests.put(url_, params={'token': token}, json=params_)
    return r.json()


def get_markers_name(robot_name):
    url_ = base_url + '/{}/markers'.format(robot_name)
    params_ = {'token': token}  # use key to set the marker type, default is 0
    r = requests.get(url_, params=params_)
    rsp = r.json()
    loc_info = rsp['results']
    markers_name = [key for key in loc_info]
    return markers_name


def get_markers(robot_name):
    url_ = base_url + '/{}/markers'.format(robot_name)
    params_ = {'token': token}  # use key to set the marker type, default is 0
    r = requests.get(url_, params=params_)
    rsp = r.json()
    return rsp


"""""
此接口已经不再开放
def move_to_location(robot_name, x, y, theta):
    url_ = base_url + '/{}/move'.format(robot_name)
    params_ = {'location':(x,y,theta),'token': token} #','.join(([x,y, theta]))
    r = requests.get(url_, params= params_)
    rsp = r.json()
    return rsp
"""""


def move_to_markers(robot_name, markers, hover_time):  # for same wait time
    url_ = base_url + '/{}/task/point_move'.format(robot_name)
    params_ = {'markers': '|'.join([mark + ',' + str(hover_time) for mark in markers]),
               'token': token}
    r = requests.get(url_, params=params_)


def cancel_move(robot_name):
    url_ = base_url + '/{}/move/cancel'.format(robot_name)
    params_ = {'token': token}
    r = requests.get(url_, params=params_)


def task_cancel(robot_name):
    url_ = base_url + '/{}/task/cancel'.format(robot_name)
    r = requests.get(url_, params={'token': token})
    return r.json()


# looks not correct based on the documents
def get_map_list(robot_name):
    url_ = base_url + '/{}/map/list'.format(robot_name)
    r = requests.get(url_, params={'token': token})
    return r.json()


"""""
此接口暂时不开放，以后可能会开放
def get_wifi_list(robot_name): #该接口没有开放
    url_ = base_url + '/{}/wifi/info'.format(robot_name)
    r = requests.get(url_, params= {'token':token})
    return r.json()
"""""


def get_current_map(robot_name):
    url_ = base_url + '/{}/map'.format(robot_name)
    r = requests.get(url_, params={'token': token})
    return r.json()


def status(robot_name):
    url_ = base_url + '/{}/robot_status'.format(robot_name)
    r = requests.get(url_, params={'token': token})
    return r.json()


def robot_status(robot_name):
    url_ = base_url + '/{}/robot_status'.format(robot_name)
    r = requests.get(url_, params={'token': token})
    rsp = r.json()
    return rsp  # rsp['results']['current_pose']


marks = ['in', 'pass0', 'in']


def error_markers(robot_name, test_times):  # 至少三个markers，最后一个最好是初始位置
    markers_info = get_markers(robot_name)
    dest_marker = marks[-1]  # 可再定义
    dest_pos = markers_info['results'][dest_marker]['pose']['position']
    dest_pos = np.array(list(dest_pos.values()))
    count = test_times
    error_list = []
    while (count):
        move_to_markers(robot_name, marks, 0)
        while (1):
            st = status(robot_name)
            move_status = st['results']['move_status']
            move_target = st['results']['move_target']
            if move_status == 'succeeded' and move_target == marks[-1]:
                break
            """""
            后期需要加上 else: sleep(time) 这个 time是自己预估的一个时间，建议取 （实际到达的时间）/2。
            """""
        st = status(robot_name)  # update again
        cur_pos = st['results']["current_pose"]
        cur_pos = np.array(list(cur_pos.values()))
        error = np.linalg.norm(cur_pos[:2] - dest_pos[:2])  # don't consider
        error_list += [error]
        print(error_list)
        count = count - 1
    df = pd.DataFrame({'errors' + str(test_times): error_list})
    df.to_csv('based_on_marker_error_list_new' + str(test_times) + '.csv')


def task_status(robot_name):
    url_ = base_url + '/{}/task/status'.format(robot_name)
    r = requests.get(url_, params={'token': token})
    return r.json()


"""""
此接口尚未开发
def position_adjust(robot_name,marker):
    url_ = base_url + '/{}/position_adjust'.format(robot_name)
    r = requests.get(url_, params={'marker' : marker, 'token': token})
    return r.json()
"""""


def joy_acc_test(robot_name, lv, av):  # 点动
    st = status(robot_name)
    pos = st['results']["current_pose"]
    pos = np.array(list(pos.values()))
    url_ = base_url + '/{}/joystick'.format(robot_name)
    r = requests.get(url_, params={'linear_velocity': lv, 'angular_velocity': av, 'token': token})
    rsp = r.json()
    while (1):
        if rsp["status"] == 'OK':  # 避免多个指令同时进行造成 混乱
            break
    time.sleep(1 / Frequency)  # 要根据它的实际频率来。存在频率误差，导致的测量误差。这个必须加。 #nov30发现
    st1 = status(robot_name)
    new_pos = st1['results']["current_pose"]
    new_pos = np.array(list(new_pos.values()))
    dist_or = "线性" if av == '0' else ("整体" if av != '0' and lv != '0' else "方位")
    print(np.linalg.norm(pos - new_pos), "点动变化", dist_or)
    return rsp


# 修改了get_yaw相关的一些可能存在的隐患
def get_yaw(ore):  # 根据{x,y,z,w}计算点的方位：目前用在计算marker的方向
    pi = 3.1416  # very important; 应该设置比实际的pi值大一点
    yaw = 2 * np.arctan2(ore[0], ore[1])
    if yaw > pi and yaw <= 2 * pi:
        yaw -= 2 * pi
    if yaw < -pi and yaw >= -2 * pi:
        yaw += 2 * pi
    return yaw


def check_dir(robot_name, mk_name):  # 计算两个点的方位差
    markers_info = get_markers(robot_name)
    mk_orient = markers_info['results'][mk_name]['pose']["orientation"]
    tar_rad = get_yaw(list((mk_orient['z'], mk_orient['w'])))
    st = status(robot_name)
    cur_rad = st['results']["current_pose"]["theta"]
    diff_rad = cur_rad - tar_rad
    print(diff_rad, "方位差（弧度）")
    return diff_rad


def check_ln_dir(robot_name, mk_name):  # 计算两个点的距离差
    st = status(robot_name)
    markers_info = get_markers(robot_name)
    st = status(robot_name)
    cur_pos = st['results']["current_pose"]
    cur_pos = list(cur_pos.values())
    tar_pos = markers_info['results'][mk_name]['pose']['position']
    tar_pos = list(tar_pos.values())
    diff_pos = np.array(tar_pos[:2]) - np.array(cur_pos[:2])
    distance = np.linalg.norm(diff_pos)
    print(distance, "距离差")
    return distance


def keep_adjst(robot_name, mk_name):  # 用于调整机器人当前方向与 点平d行
    """"
     keep moving if the distance is decrease
    """
    st = status(robot_name)
    cur_rad = st['results']["current_pose"]["theta"]
    markers_info = get_markers(robot_name)
    mk_orient = markers_info['results'][mk_name]['pose']["orientation"]
    # mk_orient = list(mk_orient.values())
    tar_rad = get_yaw(list((mk_orient['z'], mk_orient['w'])))
    diff = tar_rad - cur_rad
    # av = '-0.1' if diff >0 else '0.1' #不能太小，否则测试的时候看看是往左还是网右转; 具体数值属于调参数
    # 往左转是+， 目标在左边，那么cur - tar = negative; 目标在右边，cur - tar = positive
    degree_change('robot_4', diff)
    st = status(robot_name)
    cur_rad = st['results']["current_pose"]["theta"]
    print("调整误差(方位):", abs(cur_rad - tar_rad))


def adjust_moving(robot_name, mk_name, lv=0.1):  # 一般用于直线调整
    st = status(robot_name)
    markers_info = get_markers(robot_name)
    st = status(robot_name)
    cur_pos = st['results']["current_pose"]
    cur_pos = np.array(list(cur_pos.values()))[:2]
    tar_pos = markers_info['results'][mk_name]['pose']['position']
    tar_pos = np.array(list(tar_pos.values()))[:2]
    diff_pos = tar_pos - cur_pos
    lv = str(lv) if sum(diff_pos) > 0 else str(-lv)  # >0是在前方
    # 这个lv只能适用于在一条线上，且方向一致
    # 调参数，大的话，会影响精度，小的话会影响速度反应
    # 初期只考虑，可行性：看误差能控制到什么范围内。
    error_allow = 0.03  # 3cm， 可以调参数，不用我具体取调, 11.27, 3cm待调整
    joy_st = joy_acc_test(robot_name, lv, '0')
    # 获取初始diff_new
    if abs(np.linalg.norm(diff_pos)) > error_allow:  # 误差允许范围;需要调整
        joy_st = joy_acc_test(robot_name, lv, '0')  # Dec.01 状态已经在joy_acc_test里面判断
        st = status(robot_name)
    diff_new_pos = st['results']["current_pose"]
    diff_new_pos = tar_pos - np.array(list(diff_new_pos.values()))[:2]
    # 没有考虑自适应，自适应步长
    adj_cnt = 1  # used for evaluate time# improve can add some
    while np.linalg.norm(diff_new_pos) < np.linalg.norm(diff_pos) and np.linalg.norm(diff_new_pos) > error_allow:
        joy_st = joy_acc_test(robot_name, lv, '0')
        diff_pos = diff_new_pos
        st = status(robot_name)
        diff_new_pos = st['results']["current_pose"]
        diff_new_pos = tar_pos - np.array(list(diff_new_pos.values()))[:2]
        adj_cnt += 1
    print("调整误差（距离）：", np.linalg.norm(diff_new_pos), "adjusted times:", adj_cnt)


def adjust_dist_verticle(robot_name, mk_name, lv):  # 这个版本，不考虑方向的测试
    """""
    调整两个方向点位 （用于方向平行或者方向垂直的情况）
    使得它们之间的距离最小
    """""
    st = status(robot_name)
    markers_info = get_markers(robot_name)
    st = status(robot_name)
    # 到时候cur_pos, tar_pos 需要用标准化接口测试一下。
    cur_pos = st['results']["current_pose"]
    cur_pos = np.array(list(cur_pos.values()))[:2]
    tar_pos = markers_info['results'][mk_name]['pose']['position']
    tar_pos = np.array(list(tar_pos.values()))[:2]
    diff_pos = tar_pos - cur_pos
    diff = np.linalg.norm(diff_pos)
    joy_st = joy_acc_test(robot_name, str(lv), '0')  # 测试的时候，可以让步长大一点
    st = status(robot_name)
    cur_pos = st['results']["current_pose"]
    cur_pos = np.array(list(cur_pos.values()))[:2]
    diff_new_pos = tar_pos - cur_pos
    diff_new = np.linalg.norm(diff_new_pos)
    adj_cnt = 1
    while diff_new < diff:  # only based on distance #利用垂直距离最小，但是不知道误差范围了。
        joy_st = joy_acc_test(robot_name, lv, '0')  # 测试的时候，可以让步长大一点
        st = status(robot_name)
        diff = diff_new
        cur_pos = st['results']["current_pose"]
        cur_pos = np.array(list(cur_pos.values()))[:2]
        diff_new_pos = tar_pos - cur_pos
        diff_new = np.linalg.norm(diff_new_pos)
        adj_cnt += 1
    print(diff_new, 'adjust dist verticle', adj_cnt)


def marker_position_orient(robot_name, mk_name):  # 下周做，标准化，position 和orient接口
    """""
    获取updated marker信息
    """""
    markers_info = get_markers(robot_name)
    pos = markers_info['results'][mk_name]['pose']['position']
    pos = np.array(list(pos.values()))
    position = pos[:2]
    orient = markers_info['results'][mk_name]['pose']["orientation"]
    orient = get_yaw(list((orient['z'], orient['w'])))
    return (position, orient)


def current_position_orient(robot_name):  # 有待继续测试
    """"
    获取updated position信息
    获取updated orient信息
    """""
    st = status(robot_name)
    move_status = st['results']['move_status']
    pos = st['results']["current_pose"]
    cur_pos = np.array(list(pos.values()))[:2]
    orient = pos['theta']
    return (cur_pos, orient)


def accurate_moving(robot_name, mk_name, max_error_allowed=0.1, max_adjust_time=8):  # next week
    """""
    max_adust_time太多会导致角度偏移
    这个需要反复测试，太小的话会导致 反复微调浪费时间，甚至进入死循环
    max_error_allowed = 0.08 # 
    """""
    move_to_marker(robot_name, mk_name)
    while (1):  # 一定等待状态完成
        st = status(robot_name)
        move_status = st['results']['move_status']
        move_target = st['results']['move_target']
        if move_status == 'succeeded' and move_target == mk_name:
            break
    time.sleep(1)  # 暂停一下
    keep_adjst(robot_name, mk_name)  # 先调整方向 #这部分明天完善
    lv = 0.1  # 暂时数字 有待更改方向,只做微调
    mk_pos, mk_ore = marker_position_orient(robot_name, mk_name)
    angle = -pi / 2
    degree_change(robot_name, angle)  # there is no difference of using + or -
    cur_pos, cur_ore = current_position_orient(robot_name)
    diff_pos = np.linalg.norm(cur_pos - mk_pos)
    joy_st = joy_acc_test(robot_name, str(lv), '0')  # just once
    cur_pos, cur_ore = current_position_orient(robot_name)
    diff_new_pos = np.linalg.norm(cur_pos - mk_pos)
    lv = lv if diff_new_pos < diff_pos else - lv
    # angle_change = -angle if diff_new_pos < diff_pos else angle # diff_newpos small, 说明对了when moving to the
    adjust_dist_verticle(robot_name, mk_name, lv)
    degree_change(robot_name, -angle)  # 和angle没关
    # adjust_moving(robot_name, mk_name)
    # print(angle_change, 'ac', angle)
    # 再进行调整
    keep_adjst(robot_name, mk_name)
    error = check_ln_dir(robot_name, mk_name)
    cnt = 1
    # 最大的调整次数，避免死循环
    # 最后进行补救: Dec. 01.
    while (error > max_error_allowed):  # 对于多次校正情况下，要重新调整角度（以后这个需要做上）
        adjust_moving(robot_name, mk_name, 0.08)  # 默认情况 lv = 0.1 ; #可以设置微调步长ex. （robot_name, mk_name, lv)
        error = check_ln_dir(robot_name, mk_name)
        cnt += 1
        print("readjust:", cnt)
        if cnt > max_adjust_time:
            break
    check_ln_dir(robot_name, mk_name)
    return lv  # 暂时


"""""
这个方法还在测试中
def verticle_moving2(robot_name, mk_name):# 11/29 new strategy
    move_to_marker(robot_name, mk_name)
    while (1): #一定等待状态完成
        st = status(robot_name)
        move_status = st['results']['move_status']
        move_target = st['results']['move_target']
        if move_status == 'succeeded' and move_target == mk_name:
            break
    keep_adjst(robot_name, mk_name) #先调整方向 #这部分明天完善
    adjust_moving(robot_name, mk_name) # 两者平行且两者之间连线和方向几乎垂直
    keep_adjst(robot_name, mk_name) # 这一步在调整一次方向，尽量平行#将来考虑 加入error allow 的范围

    lv =  0.1 # 暂时数字 有待更改方向,只做微调
    mk_pos, mk_ore = marker_position_orient(robot_name, mk_name)
    angle = -pi/2
    degree_change(robot_name, angle) #there is no difference of using + or -
    cur_pos, cur_ore = current_position_orient(robot_name)
    diff_pos = np.linalg.norm(cur_pos - mk_pos)
    joy_st = joy_acc_test(robot_name,  str(lv), '0')  # just once
    while (1):
        if joy_st["status"] == 'OK':
            break
    #这里可能会产生误差，后期考虑写一个 垂直的 keep_adjust版本 #或者keep_adjust,看是90 还是0
    cur_pos, cur_ore = current_position_orient(robot_name)
    diff_new_pos = np.linalg.norm(cur_pos - mk_pos)
    lv = lv if diff_new_pos < diff_pos else - lv
    #angle_change = -angle if diff_new_pos < diff_pos else angle # diff_newpos small, 说明对了when moving to the
    #adjust_moving(robot_name, mk_name)
    adjust_dist_verticle(robot_name, mk_name, lv)
    #degree_change(robot_name, -angle) #和angle没关
    keep_adjst(robot_name,mk_name) #取代 degree_change# 提升了精度 至2cm不错。
    adjust_moving(robot_name,mk_name) #测试用dist_verticle 取代。 目前还需要两步来配合，下一步需要优化调整
    adjust_moving(robot_name,mk_name) #需要进行两次的，下一步打算，在第二个减小步长
    # 未完成，
    check_ln_dir(robot_name,mk_name)
    return lv #暂时
"""
# 粗调：定义> pi/7都是粗调
# nov. 28 角度微调
l_ang = pi / 6
m_ang = pi / 10
s_ang = pi / 13
av_lg = round(l_ang / 2, 2)
av_mid = round(m_ang / 2, 2)
av_small = 0.1


def degree_change(robot_name, rad_before, av=0.3):  # 根据目前位置转多少度，+-
    st = status(robot_name)
    orient = st['results']["current_pose"]["theta"]
    #
    # 难度在于很难确定，精度达到多少，容易造成 不断的修正导致没法停止：
    # 两个方法 判断前后最小值，第二个判断
    diff_rad = 0
    error_allowed = 0.05  # rad,计划进一步调小
    diff_rad_new = st['results']["current_pose"]["theta"] - orient
    av = l_ang / 2 if rad_before >= l_ang else (m_ang / 2 if rad_before > m_ang else
    (s_ang / 2 if rad_before > s_ang else 0.08))  # 0.08不知道是否可行
    # 关于微调可以分多个档次： 比如 pi/9< a < pi/6 和 a < pi/9两个档位。
    av = str(av) if rad_before > 0 else str(-av)  # step sice, can be adjusted
    adj_cnt = 1
    m_t = 0
    s_t = 0
    while abs(diff_rad_new - rad_before) > error_allowed:
        joy_st = joy_acc_test(robot_name, '0', av)  # just once
        # diff_rad = diff_rad_new
        st = status(robot_name)
        diff_rad_new = st['results']["current_pose"]["theta"] - orient
        diff_rad_new = diff_rad_new if diff_rad_new < 2 * pi and diff_rad_new > -2 * pi else \
            (diff_rad_new + pi * 2 if diff_rad_new < 0 else diff_rad_new - pi * 2)
        adj_cnt += 1
        diff_angle = abs(diff_rad_new - rad_before)  # 之前弄错了，要小心啊！
        if diff_angle < l_ang and diff_angle > m_ang and m_t == 0:  # 只进来一次
            m_t = 1
            av = str(av_lg) if rad_before > 0 else str(-av_lg)
            print("in large")
        #
        if diff_angle < m_ang and diff_angle > s_ang and m_t == 1:  # 只进来一次
            m_t = 2
            av = str(av_mid) if rad_before > 0 else str(-av_mid)
            print("in mid")
        if diff_angle < s_ang and s_t == 0:
            s_t = 1
            av = str(0.07) if rad_before > 0 else str(-0.07)
            print("in small")
        print((diff_rad_new - rad_before), "本次误差")
        if abs(diff_rad_new) > abs(rad_before):
            diff_rad_new = st['results']["current_pose"]["theta"] - orient
            break
    # nov 29，可以在最后一步进行微调
    # 比如如果> 0.1微调 两次左右，尽量微调到 0.1弧度以内
    # diff_rad_new 和 rad_before 都是相对于orient 的坐标系
    print(abs(diff_rad_new - rad_before), 'final')
    return abs(diff_rad_new - rad_before)


# nov 30#目前接口没有开放
def set_freq(robot):
    url_ = base_url + '/{}/request_data'.format(robot)
    r = requests.get(url_, params={'topic': 'robot_status', 'switch': 'on', 'frequency': '10', 'token': token})
    # rsp = r.json()
    print(r)


def adjust_robot_to_marker(robot_name, marker_name):
    delta = 0.1

    move_to_marker(robot_name, marker_name)

    check_ln_dir(robot_name, marker_name)


# joy_control: // 调用移动接口,机器人以角速度0.5rad/s逆时针转动，同时以线速度0.2m/s前进。
def joy_control(robot_name, lv, av):
    st = status(robot_name)
    pos = st['results']["current_pose"]
    pos = np.array(list(pos.values()))

    url_ = base_url + '/{}/joystick'.format(robot_name)
    r = requests.get(url_, params={'linear_velocity': lv, 'angular_velocity': av, 'token': token})
    rsp = r.json()

    # based on the moving time
    time.sleep(2)
    st1 = status(robot_name)
    new_pos = st1['results']["current_pose"]
    new_pos = np.array(list(new_pos.values()))
    return r.json()


# 两个向量的夹角
def intersect_angle(robot_name, pos1, pos2):# pos is np array
    cosin = pos1*pos2/ (np.linalg.norm(pos1) * np.linalg.norm(pos2))
    ang = np.arccos(cosin)
    return ang


def get_robot_position(robot_name):
    st = status(robot_name)
    robot_pos = st['results']["current_pose"]
    return robot_pos

def robot_marker_angle(robot_name, marker_name):
    st = status(robot_name)
    robot_pos = st['results']["current_pose"]
    robot_pos = np.array(list(robot_pos.values()))

    marker_pos, marker_ori = marker_position_orient(robot_name, marker_name)
    ang = intersect_angle(robot_name, robot_pos, marker_pos)


def get_marker_orientation(robot_name, marker_name):
    markers = get_markers(robot_name)
    orientation = markers['results'][marker_name]['pose']["orientation"]
    return orientation


def get_marker_position(robot_name, marker_name):
    markers = get_markers(robot_name)
    position = markers['results'][marker_name]['pose']["position"]
    return position


# 标注点的方向角
def get_marker_angle(robot_name, marker_name):
    mk_orient = get_marker_orientation(robot_name, marker_name)
    mk_orient = list(mk_orient.values())
    angle = get_yaw(mk_orient)
    return angle


def move_to_marker(robot_name, marker_name):
    url = base_url + '/{}/move'.format(robot_name)
    params = {'marker': marker_name, 'token': token}

    resp = requests.get(url, params=params)
    print('move_to_marker response:', resp)


def move_to_marker_until_ok(robot_name, marker_name):
    move_to_marker(robot_name, marker_name)

    while True:
        st = status(robot_name)
        move_status = st['results']['move_status']
        move_target = st['results']['move_target']
        if move_status == 'succeeded' and move_target == marker_name:
            break
        else:
            time.sleep(0.5)


def get_robot_to_marker_vector(robot_name, marker_name):
    mk_pos = get_marker_position(robot_name, marker_name)
    rb_pos = get_robot_position(robot_name)

    return np.array([(mk_pos['x'] - rb_pos['x']), (mk_pos['y'] - rb_pos['y'])])


def get_robot_to_marker_vector_angle(robot_name, marker_name):
    vec_x, vec_y = get_robot_to_marker_vector(robot_name, marker_name)

    angle = np.arctan2(vec_y, vec_x)

    print('get_robot_to_marker_vector_angle:', angle)
    return angle


def get_robot_theta(robot_name):
    theta = get_robot_position(robot_name)['theta']

    print('get_robot_theta', theta)
    return theta


def get_unit_vector(angle):
    vec_y = np.sin(angle)
    vec_x = np.cos(angle)
    return np.array([vec_x, vec_y])


def cos_np(vec1, vec2):
    return np.dot(vec1, vec2)/(np.linalg.norm(vec1)*(np.linalg.norm(vec2)))


def adjust_robot(robot_name, marker_name):
    mv_vec = get_robot_to_marker_vector(robot_name, marker_name)
    mv_theta = np.arctan2(mv_vec[1], mv_vec[0])

    rb_theta = get_robot_theta(robot_name)
    rb_vec = get_unit_vector(rb_theta)

    cos = cos_np(mv_vec, rb_vec)

    mv_theta_p = mv_theta if mv_theta > 0 else 2 * np.pi + mv_theta
    rb_theta_p = rb_theta if rb_theta > 0 else 2 * np.pi + rb_theta

    diff_angle = mv_theta_p - rb_theta_p
    # 机器人转到正向
    if cos > 0:
        if diff_angle > 0:
            pass  # 左转
        else:
            pass  # 右转
    # 转到反向
    else:
        if diff_angle > 0:
            pass  # 右转
        else:
            pass  # 左转

