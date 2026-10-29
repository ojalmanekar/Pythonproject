# PROCEDURAL
rex = {"name":"Rex", "sound":"Woof"}
tom = {"name":"Tom", "sound":"Moew"}

def speak(pet):
    print(f"{pet["name"]} says {pet["sound"]}")

#speak(rex)
#speak(tom)

#CLASS
class Animal:
    def __init__(self, name, sound, kind=""):
        self.name = name
        self.sound = sound
        self.kind = kind
    def speak(self):
        print(f"{self.name} say {self.sound}")
    def __str__(self):
        return f"I am a {self.kind}"
    
    

#rex_obj = Animal("Rex","Woof","Dog")
#tom_obj = Animal("Tom","Meow","Cat")
#rex_obj.speak()
#tom_obj.speak()
#print(rex_obj)
#print(tom_obj)


class Customer:
    def __init__(self, name, visits=0):
        self.__name = name
        self.visits = visits
    def __str__(self):
        return f"{self.__name}: {self.visits} visits."
    def set_name(self, name):
        if name != "":
            self.__name = name

    def set_visits(self, visits):
        if visit >= 0:
            self.visits = visits
    def get_name(self):
        return self.__name

#ada = Customer("Ada", 4)
#print(ada)
#bob = Customer("Bob")
#print(bob)
#
##ada.__name = "Celina"
##print(ada.__name)
#
#ada.set_name("")
#print(ada.get_name())

#from cafe_w7 import Register, Order, Drink

#register = Register(0.0, {"latte": 50})
#
#five = Order()
#sixty = Order()
#five.add(Drink("latte", 3.2), 5)
#sixty.add(Drink("latte", 3.2), 60)
#print(register.get_stock("latte"))
#print(register.get_cash())
#print(register.sell(five))
#print(register.get_stock("latte"))
#print(register.get_cash())
#print(register.sell(sixty))
#print(register.get_stock("latte"))
#print(register.get_cash())
#print(register.sell(five))
#print(register.get_stock("latte"))
#print(register.get_cash())

#from cafe_w7 import Cafe
#register = Cafe(cash=0.0).register
#print(register.get_stock("muffin"))
#register.restock("muffin", 5)
#print(register.get_stock("muffin"))
#register.restock("muffin", -5)
#print(register.get_stock("muffin"))
#print(register.get_stock("potatoes"))
#register.restock("potatoes", 5)
#print(register.get_stock("potatoes"))