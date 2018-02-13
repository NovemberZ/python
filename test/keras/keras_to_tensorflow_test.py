#coding=utf-8

import tensorflow as tf

import numpy as np
import cv2

from skimage.io import imread

test_img_path = "test1.jpg"

rows, cols = 32, 32

test_img = cv2.resize(imread(test_img_path, as_grey=True), (cols, rows), interpolation=cv2.INTER_AREA)

test_img = np.array(test_img)

test_img = test_img.reshape(1, 32, 32, 1).astype('float32')/255

TF_graph_file = '/Users/jammy/KerasModel/tensorflow_model/elevatorDigitsRecognize32TF'

new_input = tf.placeholder(tf.float32, shape=[None, 32, 32, 1])

with open(TF_graph_file, 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    output = tf.import_graph_def(graph_def, return_elements=['output_node0:0'])

with tf.Session() as sess:
    #


    #print(sess.run(output))  #直接运行该句会报错，告诉我们输入节点没有给数据，由此知道输入节点的数据
    print(sess.run(output, feed_dict={'import/conv2d_1_input:0':test_img}))