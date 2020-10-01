import tensorflow as tf
import numpy as np

x_data=np.random.rand(6).astype(np.float)
y_data=x_data*0.1+0.3

Weights = tf.Variable(tf.random.uniform([1],-1,1))
biases = tf.Variable(tf.zeros([1]))
# print(Weights.value())
# print(biases.value())

y = Weights*x_data+biases
diff = tf.square(y-y_data)
loss = tf.reduce_mean(diff)
optimizer = tf.compat.v1.train.GradientDescentOptimizer(0.5)
train = optimizer(loss)
print(type(diff))
print(type(loss))
# print(Weights)