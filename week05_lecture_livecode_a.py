#list = []
#tuple = ()
#dictionary = {}
#

#dict()
#string1 = "string1"
#string2 = "string2"
#
#string2 = string1
#
#list1 = [1,2]
#list2 = []
#
#print(f"list1 {list1}")
#print(f"list2 {list2}")
#
#list2 = list1
#
#print(f"reassigned list2 {list2}")
#
#list1.append(3)
#
#print(f"appended list1 {list1}")
#
#print(f"appended list2 {list2}")


#print(id(3.14), id(3.14))
#
#print(id(3.14))
#
#price1 = 3.14
#
#print(id(price1-3))
#
#print(id(price1-3))


#a = [1,2,3]
#b = a
#c = list(a)

#print(f"id(a): {id(a)}")
#print(f"id(b): {id(b)}")
#print(f"id(c): {id(c)}")
#
#b.append(4)
#c.append(5)
#
#print(f"id(a): {id(a)}, content: {a}")
#print(f"id(b): {id(b)}, content: {b}")
#print(f"id(c): {id(c)}, content: {c}")
#
#print(f"id(c[3]), {id(c[3])}, {c[3]}")
#print(id(5))

#print(id([1, 2, 3, 5]))
#
#print(id(4))
#
#template = "closed"
#print(f"template init: {id(template)}, content: {template}")
##
#sign = "closed"
#print(f"sign after: {id(sign)}, content: {sign}")
#
#sign = template
##
#print(f"template after: {id(template)}, content: {template}")
#print(f"sign after: {id(sign)}, content: {sign}")
##
#sign = 4
#print(f"sign after: {id(sign)}, content: {sign}")
##
#print(f"template after: {id(template)}, content: {template}")

#import cafe_w5

#from register_sayings import *

#
#print(welcome("Romain"))

#def welcome(name):
#    return f"Goodbye, {name}!"
#
#print(welcome("Romain"))


#import register_sayings
#
#print(register_sayings.welcome("Romain"))
#
#print(welcome("Romain"))

#import register_sayings

#try:
#    5/0
#except (ZeroDivisionError, SyntaxError, ):
#    print("error division zero")
#
#    import sys

#print(10/3)
#
#print(10/3 - 3.33)
#
#assert (10/3 - 3.33) < 0.01