import numpy as np

oneD_arr = np.array([1,2,3,4,5])
# [1 2 3 4 5]

twoD_arr = np.array([[1,2,3], [4,5,6]])
# [[1 2 3]
#  [4 5 6]]

zeroes_arr = np.zeros(4)
# [0. 0. 0. 0.]

ones_arr = np.ones((3,2))
# [[1. 1.]
#  [1. 1.]
#  [1. 1.]]

range_arr = np.arange(5, 12)
# [ 5 6 7 8 9 10 11]

random_arr = np.random.randint(low=50, high=101, size=(2,3))
# [[ 80 86 50]
#  [ 75 100 61]]

range_arr += 2
# [ 7 8 9 10 11 12 13]

twoD_arr *= 3
# [[ 3  6  9]
# [12 15 18]]
