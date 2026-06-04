from menu import Menu
from coffee_maker import CoffeeMaker
from money_machine import MoneyMachine

cm = CoffeeMaker()
m = Menu()
mm = MoneyMachine()

is_on = True
while is_on:
    choice = input(f"What would you like?({m.get_items()}):")
    if choice == "off":
        is_on = False
    elif choice == "report":
        print(cm.report())
        print(mm.report())
    else:
        drink = m.find_drink(choice)
        if cm.is_resource_sufficient(drink) and mm.make_payment(drink.cost):
            print(cm.make_coffee(drink))