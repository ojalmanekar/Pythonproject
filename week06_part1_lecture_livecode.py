#import register_sayings as reg

#print(reg.goodbye)

import numpy as np

#my_list = [12.1, 6.4, 15.8, 3.4]

#print(f"my_list: {my_list}, {type(my_list)}")
#
#my_array = np.array(my_list)
#
#print(f"my_array: {my_array}, {type(my_array)}")
#
#my_array

#my_array = np.array([2.5, 3.2, 3, 2.8, 2.4, 2.2])
#
#print(my_array.max())
#print(my_array.argmax())
#print(my_array.sum())
#print(f"{my_array.mean():.3f}")
#print(len(my_array))

#my_list = [12, 6.4, 15.8, 3.4]
#my_list = [12.0, 6, 15, 3]

#my_list = [0, "one", "two"]
#print(my_list)

#my_array = np.array(my_list)
#print(my_array)


#my_list = [0, 1, "two"]
#print(my_list)
#my_array = np.array(my_list)
#print(my_array)
#
#print(my_array * my_array)
#
#print(my_array[0], type(my_array[0]))
#print(my_array[1], type(my_array[1]))

#quantities = np.array([2,1,3])
#prices = np.array([2.5,3.2,2.4,2.5])
#
#line_totals = quantities * prices
#
#print(line_totals)

#var1 = 1 #ref1 
#var2 = 2 #ref2
#var3 = 3 #ref3
#
##.      ref1    ref2  ref3
#list1 = [1,       2,    3] # [ref1, ref2, ref3] -> ref4
#
##.       ref4
#list2 = list1 
#
#print(list1)
#print(list2)

#          ref5
#list2[0] = 10 #[ref5, ref2, ref3] -> ref4
#
#print(list2)
#print(list1)
#
#list2 = list(list1) #[ref5, ref2, ref3] -> ref6
#
#list2[0] = 5 #ref7
#
#print(list2) #[ref7, ref2, ref3]
#print(list1) #[ref5, ref2, ref3] 
#
#
#print(5) # ref7
#
#list1[0] = list2
#
#print(list1)

#for e in [1,2,3]:
#    print(e)
#
#print(id([1,2,3]))
#var1 = [e for e in [1,2,3]][:]
#print(id(var1))
#
#print([1,2,3], var1)

#print([[1,2,3],[4,5]])

#one_d = np.arange(6)
#two_d = np.reshape(one_d, (2,3))
#
#print(one_d)
#print(two_d)
#
#one_d[0] = 9
#two_d[1][1] = 0
#
#print(one_d)
#print(two_d)

#grid = np.genfromtxt("data/hourly_items.csv", skip_header=1, #delimiter=",")
#
#print(type(grid))
#print(grid)
#
#print(grid[0])
#
#print(grid[:, 0])
#
#print(grid[4 ,5:])
#
#print(grid[1:4, 4:6])
#
#print(grid[2,3])

#x = np.genfromtxt("data/transactions.csv", skip_header=1, delimiter=",#")
#
#print(type(x))
#
#print(x[:3])
#
#var = x @ x
#print(var[:3])

#print(np.ones((2,5)))
#
#print(np.ones((2,5,3,2,2,2,3,3)))

#[0,1,2,3,4,5]

#[[0,1,2],[3,4,5]]

#print(np.ones((10,1)))