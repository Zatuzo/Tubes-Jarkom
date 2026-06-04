class Animal:
    def __init__(self, name):
        self.name = name
        
    def sound(self):
        print("making a sound")
        
class Dog(Animal):
    def __init__(self, name, breed, age):
        super().__init__(name)
        self.breed = breed
        self.age = age
        
    def sound(self):
        super().sound()
        print("Woof!")
        
mydog = Dog("Jackson", "Labrador", 3)

mydog.sound()      