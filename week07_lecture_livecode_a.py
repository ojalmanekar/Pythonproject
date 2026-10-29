# PROCEDURAL
#rex = {"name": "Rex", "sound": "Woof"}
#rom = {"name": "Tom", "sound": "Meow"}
#
#def speak(pet):
#    print(f"{pet["name"]} says {pet["sound"]}")

#speak(rex)


# CLASS
class Animal:
    def __init__(self, name, sound):
        self.name = name
        self.sound = sound
    def speak(self):
        print(f"{self.name} says {self.sound}")
    def __str__(self):
        return f"I am a {self.name} and I made this sound {self.sound}"

rex_obj = Animal("Rex", "Woof")
tom_obj = Animal("Tom", "Moew")
rex_obj.speak()
tom_obj.speak()


print(id(rex_obj))
print(id(tom_obj))
#rex_obj.speak()
#print(rex_obj)
#print(rex_obj.sound)
#rex_obj.sound = "HAHAHAHA"
#print(rex_obj.sound)

#print(rex_obj, type(rex_obj))
#print(rex_obj.name, type(rex_obj.name))

class Customer:
    def __init__(self, name, visits=0):
        self.name = name
        self.visits = visits

    def __str__(self):
        return f"{self.name}: {self.visits} visits."

#ada = Customer("Ada", 4)
#print(ada)
#bob = Customer("Bob")
#print(bob)

#class Animal:
#    def __init__(self, name, sound):
#        self.name = name
#        self.__sound = sound
#    def speak(self):
#        print(f"{self.name} says {self.__sound}")
#    def __str__(self):
#        return f"I am a {self.name} and I made this sound {self.__sound}"
#
#rex_obj = Animal("Rex", "Woof")
#print(rex_obj.__sound)
#print(rex_obj.__sound,type(rex_obj.__sound))


#import cafe_w7 as Cafe

#print(Cafe.__name__)

#reg = Cafe.Cafe(cash=0.0).register
#print(reg.get_stock("muffin"))
#reg.restock("muffin", 5)
#print(reg.get_stock("muffin"))
#
#print(reg.get_stock("postcards"))
#reg.restock("postcards", 5)
#print(reg.get_stock("postcards"))