#count = 0
#
#while count != 5: 
#    count = count + 1 #runs only when it's true
#    print(count)
#
#print(count)


#list_of_ones = [1,"one","i", True]

#print(list_of_ones)

#list_of_ones[1] = "two"
#
#print(list_of_ones)
#
#list_of_ones[1] = 2
#
#print(list_of_ones)
#
#print(list_of_ones[-1])

#index = 1
#list_of_ones[index] = list_of_ones[index] * 2
#
#print(list_of_ones, len(list_of_ones))
#
#del list_of_ones[2]
#
#print(list_of_ones, len(list_of_ones))
#
#list_of_ones.append("romain1")
#list_of_ones.append("romain2")
#list_of_ones.append("romain3")
#list_of_ones.append("romain4")
#
#print(list_of_ones)
#
#list_of_ones.pop()
#
#print(list_of_ones)
#
#print([0]*5)

#string = "the latte was excellent and the milk was perfect"

#print(string.split())

#sys_argv = ["program.py", "arg1", "arg2"]
#
#print(sys_argv)
#
#pname, args = sys_argv[0], sys_argv[1:]
#
#print(pname)
#print(args)

#               0.       1       2.   3.  4.    5
positions = ["first", "middle", "6", "8", "5", "last"]
#print("midpoint", positions[len(positions) // 2])

#print(type(" ".join(positions)))

#print("-".join(positions))

#           [0,1,2,3,4]
#for i in range(5):
#    print(i)

#count=0
#for e in positions:
#    print(count, e)
#    count+=1
#
#for e in enumerate(positions):
#    print(e)
#
#for index, element in enumerate(positions):
#    print(index, element)


#quantities = [2,0,4]
#prices = [.4,12.2,5]
#
#quantities.pop()
#
#for i in range(len(quantities)):
#    print(quantities[i],prices[i])

#list_names = ["romain", "grace", "ada", "bob", "romain"]

#print(list_names)
#
#set_names = {"romain", "grace", "ada", "bob", "romain"}
#
#print(set_names)
#print(set_names)
#print(set_names)
#
#del set_names
#
#set_names = {"romain", "grace", "ada", "bob", "romain"}
#
#print(set_names)

#set_names = {"romain", "grace", "ada", "bob", "romain"}
#
#set_names.add("Romain".lower())
#
#print(set_names)
#
#set_names.remove("Romain".lower())
#
#print(set_names)
#
#set_names.remove("Romain".lower())

#single = "espresso",
#print(type(single))
#not_a_tuple = ["pototo"]
#print(type(not_a_tuple))
#not_a_tuple[0] = "dog"
#print(not_a_tuple)
#
#
#single = "potato",
#print(type(single))
#
#single[0] = "dog"

#a,b,c = (1,2,3)
#print(a,b,c)
#
##?,? = 2,1
#a,b = b,a 
#
#print(a,b,c)


dict = {"coffee":2, "water":1, "muffin":5}

dict["tea"] = 6
#
#print(dict["tea"])
#
#dict["tea"] = "test"
#print(dict["tea"])

#print(dict.keys())
#print(dict.values())

#print("the latte was excellent and the milk was perfect")

#print("   the latte was excellent and the milk was perfect \n".strip())

#print("latte,the latte was excellent and the milk was perfect".split(","))

print("love,0.9".split(","))