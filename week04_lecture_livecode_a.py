#count = 0

#while count != 5: 
#    count = count + 1 #runs only when it's true

#print(count)

#bestseller = ["latte", "espresso", "muffin", "cappuccino", "tea"]

#print(bestseller[2]) #muffin

#print(bestseller[1:2])

#print("latte"[4])

#var = 1
#print(var)

#var = "one"
#print(var)
#print(type(var))
#       0    1     2
#list = [1, "one", "i"]
#
#print(list)
#
#list[1] = 2
#print(list[1])
#
#print(list)

#               0           1           2       3           4
#bestseller = ["latte", "espresso", "muffin", "cappuccino", "tea"]

#print(bestseller[:2])

#print(list("espresso"))

# ['e', 's', 'p', 'r', 'e', 's', 's', 'o']

#print("espresso"[:3])

#                 0  1   2   3
daily_revenue = [2.3,.2,5.4,1.5]

#print(daily_revenue)

#print(daily_revenue[3]*2)

#print(daily_revenue[3])

#daily_revenue[3] = daily_revenue[3] * 2

#print(daily_revenue[3])

#print(daily_revenue)
#
#print(len(daily_revenue))
#
#del daily_revenue[1]
#
#print(daily_revenue)
#
#print(len(daily_revenue))

#row = []

#print(row)

#bestseller = ["latte", "espresso", "muffin", #"cappuccino", "tea"]
#
#print(bestseller)
#print(len(bestseller))
#
#bestseller.append("cookie1")
#bestseller.append("cookie2")
#bestseller.append("cookie3")
#bestseller.append("cookie4")
#
#print(bestseller)
#print(len(bestseller))
#
#bestseller.pop()
#print(bestseller)
#print(len(bestseller))
#
#for product in bestseller:
#    print(product)
#
#increased_bestseller_in_the_middle = bestseller[:2] + #["whatever"] + bestseller[2:]
#
#print(bestseller)
#print(increased_bestseller_in_the_middle)
#
#del increased_bestseller_in_the_middle[2]
#print(increased_bestseller_in_the_middle)
#
#increased_bestseller_in_the_middle.pop()
#print(increased_bestseller_in_the_middle)

#a, b = 1, 2
#
#c, d = 3, 4
#
#print(a,b)
#print(c,d)

#program_name, list_of_arguments = "cafe.py", ["romain",2,3213.323,True][1:]

#print(program_name)
#print(list_of_arguments)

review = "espresso,great espresso but the service was slow"

#print(str(review.split(",")).split())
#print(list(review))

#print(str(review.split()).split(",")[0])

#rebuilt_review = []
#for product in review.split():
#    print(product.split(","))
#    rebuilt_review += product.split(",")
#
#print(rebuilt_review)

#print(["tic"]+["tac"]+["toe"])
#print(type("".join(["tic","tac","toe"])))
#print(" ".join(["tic","tac","toe"]))
#print("-".join(["tic","tac","toe"]))

#bestseller = ["latte", "espresso", "muffin", #"cappuccino", "tea"]
#
#for e in bestseller:
#    print(e)
#
#for index, product in enumerate(bestseller):
#    print(index, product)

#quantities = [2,0,4]
#prices = [1.2,.5,.6]

#print(quantities)
#print(prices)
#
#prices.pop()
#
#print(quantities)
#print(prices)
#
#for i in range(len(quantities)):
#    print(quantities[i])
#    print(prices[i])

#list = [] #keep the order
#set = {} #you do NOT keep the order
#
#regulars = {"ada", "grace", "romain"}
#regulars.add("bob")
#
#print(regulars)
#
#regulars.add("bob")
#
#print(regulars)
#
#regulars.remove("romain")
#
#print(regulars)
#
#regulars.remove("romain")

#print(regulars)

#dict = {"romain":10000000}
#
#print(dict)
#
#dict["ada"] = "one"
#
#print(dict)
#
#dict["ada"] = 2.0
#
#print(dict)
#
#del dict["romain"]
#
#print(dict)

#print({x: x**2 for x in range(5)})

#prices = {"coffe":2,"espress":3}
#
#print(prices.keys())
#
#print(prices.values())

#regulars = {"ada", "grace", "romain"}
#
#print(regulars)
#
#del regulars
#
#regulars = {"ada", "grace", "romain"}
#
#print(regulars)

#a, b, c = (1,2,3)

#print(a, b, c)

#a,b,c = a,c,b
#print(a, b, c)