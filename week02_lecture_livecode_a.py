
latte_price = 3.20
latte_qty = 3

#print("""
#jdlkasjd
# dsas das das
# d as
#                    d 
# asd 
# as
# d as
# d 
# asd aj s    a as as d asd dsa 
#""")

"""
print("The total is"+ " " + str(latte_price*latte_qty))

print("total", latte_price * latte_qty, sep='????')

print(latte_qty)


print(f"total with fstring: {latte_price*latte_qty} and????i love èpotatos")

print(f'fixed total from ugliness: {latte_price*latte_qty:.2f}')
"""

#string_test = "asjhdkaj = {:e}"
#print(type(string_test))

#print("asjhdkaj = {}".format(latte_qty))

#print(string_test.format(latte_price))

#print(f"total in digit {latte_price*latte_qty:d}")

'''
cool_symbol = "%"
num_stars = 10
cofe_name = " The Daily Grind Coffee shop "
print(cool_symbol*num_stars+cofe_name+cool_symbol*num_stars + "\n\n")

print(len(cofe_name))
cofe_print_len = len(cofe_name)
computed_len = cofe_print_len + 2*num_stars
print(f"{cofe_name}")
print(f"{cofe_name:{cool_symbol}^{computed_len}}")

print("cooffee total \t 45")
print("cofe \t 45")

print(f"{cofe_name:^10}")
'''

#print("|{0:-^12}|".format("Center"))

#user_name = ""
#user_name = input("your name: ")
#print(f"{user_name}")

#print(f"Hello, {input("What is your name? ")}, i am pleased to meet you!!!!")

'''
year_of_visit = int(input("which year did you visit us?"))
print(type(year_of_visit))
print(f"you came {2026-year_of_visit} years ago.")
'''
#import register_sayings

#cashier = input("Cashier name: ")
#print(register_sayings.welcome(cashier))

#espresso_qty = int(input("How many espressos? "))
#latte_qty = int(input("How many lattes? "))
#muffin_qty = int(input("How many muffins? "))
'''
menu = open("menu.txt","r")
print(menu.tell())
print(menu.readline())
print(menu.tell())
print(menu.readline())
print(menu.tell())
menu.seek(27)
print(menu.readline())
menu.close()
#print(menu.read())
'''

#total= 2.2
#revenue_file = open("revenue.txt","w")
#revenue_file.write(f"{total:.2f}")
#revenue_file.close()

#revenue_file = open("revenue.txt","a")
#revenue_file.write(f"\n4.50")
#revenue_file.close()

#log = open("revenue.txt","r")
#print(log.read())
#log.close()

#print("this is","a cool print")

global var
var = 2

def price(qty=0, var=var):
  print(f"the quantity is {qty}")
  print(var)
  var = 5
  print(var)
  return qty>var

print(var)

#price(10)
print(price(2))
