import tensorflow as tf
import numpy as np


tf.compat.v1.disable_eager_execution()
x_data=np.random.rand(6).astype(np.float32)
y_data=x_data*0.1+0.3
# print(type(y_data))
# print(y_data,'_____')
Weights = tf.Variable(tf.random.uniform([1],-1,1))
# print(type(Weights))
# print(Weights,']]]]]]]]]')
biases = tf.Variable(tf.zeros([1]))
# print(Weights.value())
# print(biases.value())

y = Weights*x_data+biases
#print(type(y))
#print(y,'*******')
diff = tf.square(y-y_data)
#print(type(diff))
#print(diff,'----')
loss = tf.reduce_mean(diff)
#print(type(loss))
#print(loss,'=====')
# loss = tf.reduce_mean(tf.square(y-y_data))
optimizer = tf.compat.v1.train.GradientDescentOptimizer(0.5)
train = optimizer.minimize(loss)
# print(type(diff))
# print(type(loss))
# print(Weights)

# init = tf.compat.v1.initialize_all_variables()
init = tf.compat.v1.global_variables_initializer()
sess=tf.compat.v1.Session()
sess.run(init)

for step in range(201):
    sess.run(train)
    if  step %20 ==0:
        print(step,sess.run(Weights),sess.run(biases))
