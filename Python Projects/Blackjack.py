import random

def calculate(hand):
    total = sum(hand)
    aces = hand.count(11)
    
    while total > 21 and aces:
        total -= 10
        aces -= 1
    
    return total

def show_hand():
    print("\nYour cards:", my_hand, "| Your score:", MP)
    print("Bot's cards:", bot_hand, "| Bot's score:", BP)

def lose():
    print("\nYou lose!")
    show_hand()

def win():
    print("\nYou win!")
    show_hand()

cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

my_hand = [random.choice(cards), random.choice(cards)]
bot_hand = [random.choice(cards)]

MP = calculate(my_hand)
BP = calculate(bot_hand)

show_hand()

while MP < 21:
    action = input("\nHit(H) or Pass(P)?: ").upper()
    if action == "H":
        my_hand.append(random.choice(cards))
        MP = calculate(my_hand)
        show_hand()
        if MP > 21:
            lose()
            exit()
    elif action == "P":
        break
    else:
        print("Invalid input! Please enter 'H' or 'P'.")

while BP < 17:
    bot_hand.append(random.choice(cards))
    BP = calculate(bot_hand)

if BP > 21 or MP > BP:
    win()
elif MP < BP:
    lose()
else:
    print("\nIt's a tie!")
    show_hand()
