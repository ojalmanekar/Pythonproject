#print("hello"+" "+"world"+"!"*30)

#print("hello","world","Romain","i","hope",sep=" % ")

user_name = "Romain"
user_age = 18
user_birthyear = 2000

#print("hello"+user_name+str(user_age))
#print("hello",user_name,"you age is",user_age)

#print(f"hello world {user_name} your age is {2026-user_birthyear}")

#print(f"{10/3:.2f}")

symbol = "%"
num_symbols = 6
coffeeshop_name = " my coffee shop "
opening_phrase = symbol*num_symbols+coffeeshop_name+symbol*num_symbols
#print(len(opening_phrase))
#print(opening_phrase)

#print(f"{coffeeshop_name:{symbol}>40}")

#print("aslk \t asddasd")

#print(("|{0:-^12}|").format("Center"))

#user_name = input("What is your name? ")

#print(f"Oh cool, your name is {user_name}")

current_year = 2026
#print(type(input("provide a number: ")))
#print(f"you age is then {current_year-int(input("what is your year of birth"))}")

#import register_sayings

#print(register_sayings.welcome("Romain"))

#print(register_sayings.goodbye)

#my_file = open("menu.txt","r")
#print(my_file.read(20))
#print(my_file.tell())
#print(my_file.readline())
#print(my_file.tell())
#print(my_file.readline())
#print(my_file.tell())
#my_file.seek(27)
#print(my_file.tell())
#print(my_file.readline())
#print(my_file.tell())
#my_file.close()

#import sys

#total = 6
#revenue_file_name = "revenue.txt"
#print(f"default name of file {revenue_file_name}")
#revenue_file_name = sys.argv[1]
#total = int(sys.argv[2])
#print(f"argument name of file {revenue_file_name}")
#revenue = open(revenue_file_name,"w")
#revenue.write(f"The total is : {total:.2f}\n")
#revenue.close()
#
#log = open(revenue_file_name,"r")
#print(log.read())

#def compute_discount(value):
#    #print(value*90/100)
#    return value*10/100
#    
#
#def is_good_discount(value):
#    return value > 5
#
#discounted_total = compute_discount(int(input("what is the #total? ")))
#print(discounted_total)
#
#print(f"is it a good price: {is_good_discount#(discounted_total)}")


#threshold_big_number = 300
#print(threshold_big_number)

#def is_this_a_big_number(value):
#    #print(threshold_big_number)
#
#    threshold_big_number = 100
#
#    print(threshold_big_number)
#
#    return value > threshold_big_number
#
#print(threshold_big_number)
#
#print(is_this_a_big_number(200))


def euros_and_cents(amount):
    whole = amount // 1.0
    return whole, amount - whole

#print(euros_and_cents(2.3))

euros, cents = euros_and_cents(2.3)

print(euros)
print(cents)