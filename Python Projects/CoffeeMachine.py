def report():
    print(f'Water: {resources["water"]}ml')
    print(f'Milk: {resources["milk"]}ml')
    print(f'Coffee: {resources["coffee"]}g')

def process_coins():
    total = 0
    total += int(input("How many Quarters?:")) * 0.25
    total += int(input("How many Dimes?:")) * 0.10
    total += int(input("How many Nickel?:")) * 0.05
    total += int(input("How many Pennies?:")) * 0.01
    return total



MENU = {
    "espresso": {
        "ingredients": {
            "water": 50,
            "coffee": 18,
        },
        "cost": 1.5,
    },
    "latte": {
        "ingredients": {
            "water": 200,
            "milk": 150,
            "coffee": 24,
        },
        "cost": 2.5,
    },
    "cappuccino": {
        "ingredients": {
            "water": 250,
            "milk": 100,
            "coffee": 24,
        },
        "cost": 3.0,
    }
}

resources = {
    "water": 300,
    "milk": 200,
    "coffee": 100,
}

is_on = True

while is_on:
    choice = input("What would you like? (espresso/latte/cappuccino): ").lower()

    if choice == "report":
        report()

    elif choice == "off":
        is_on = False

    elif choice in MENU:
        ingredients = MENU[choice]["ingredients"]
        enough = True
        
        for bahan in ingredients:
            if ingredients[bahan] > resources[bahan]:
                print(f"Sorry there is not enough {bahan}.")
                enough = False
        
        if not enough:
            continue

        payment = process_coins()

        if payment < MENU[choice]["cost"]:
            print("Sorry that's not enough money. Money refunded.")
            continue
        else:
            change = round(payment - MENU[choice]["cost"], 2)
            if change > 0:
                print(f"Here is ${change} in change.")

            for bahan in ingredients:
                resources[bahan] -= ingredients[bahan]

            print(f"Here is your {choice}. Enjoy!")

    else:
        print("Invalid choice.")