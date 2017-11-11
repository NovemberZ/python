import tensorflow as tf
import numpy as np

hello = tf.constant('Hello, TensorFlow!')
session = tf.Session()
print(session.run(hello))

print(np.version.version)

print()
