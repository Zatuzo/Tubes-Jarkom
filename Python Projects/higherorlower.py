import random
dice = [1, 2, 3, 4, 5, 6]

action = input("Do you want to play(P) or exit(E)?").upper()
while action != "E":
    score = 0
    while score >= 0:
        dice1 = random.choice(dice)
        dice2 = random.choice(dice)
        while dice2 == dice1:
            dice2 = random.choice(dice)
    
        print(f"the number is {dice1}")
        guess = input("Do you think the next number is higher(H) or lower(L)?:").upper()
        if guess == "H" and dice2 > dice1:
            print("You are correct")
            score += 1
        elif guess == "L" and dice2 < dice1:
            print ("You are correct!")
            score += 1
        else:
            print("You are incorrect!")
            print(f"Your score was {score}")
            score = -1
    action = input("Play again(P) or Exit(E)?:").upper()