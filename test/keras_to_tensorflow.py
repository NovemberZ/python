#coding = utf-8

from keras.models import load_model
import tensorflow as tf
from tensorflow.python.framework import graph_io
import os
from keras import backend as K

##set parameters
input_file_path ='/Users/jammy/KerasModel/' # input file path
weight_file ='elevatorDigitsRecognize32.h5'       # keras model file name  located inside input file path
num_output = 1
write_graph_def_ascii_flag = True
prefix_output_node_names_of_final_network = 'output_node'
output_graph_name ='elevatorDigitsRecognize32TF'

output_file_path = input_file_path + 'tensorflow_model/'
if not os.path.isdir(output_file_path):
    os.mkdir(output_file_path)

weight_file_path = os.path.join(input_file_path, weight_file)

# load keras model and rename output
K.set_learning_phase(0)
net_model = load_model(weight_file_path)

pred = [None]*num_output
pred_node_names = [None]*num_output

input = tf.identity(net_model.input, name="input_node")

for i in range(num_output):
    pred_node_names[i] = prefix_output_node_names_of_final_network + str(i)
    pred[i] = tf.identity(net_model.output[i], name=pred_node_names[i])
print("output nodes names are:", pred_node_names)

# write graph definition in ascii
sess = K.get_session()

if write_graph_def_ascii_flag:
    f = 'only_the_graph_def.pb.ascii'
    tf.train.write_graph(sess.graph.as_graph_def(), output_file_path, f, as_text=True)
    print('save the graph definition in ascii format at:', os.path.join(output_file_path, f))

# convert variables to constants and save
constant_graph = tf.graph_util.convert_variables_to_constants(sess,
                                         sess.graph.as_graph_def(), pred_node_names)

graph_io.write_graph(constant_graph, output_file_path, output_graph_name, as_text=False)
print('save the constant graph (ready for inference) at:', os.path.join(output_file_path, output_graph_name))