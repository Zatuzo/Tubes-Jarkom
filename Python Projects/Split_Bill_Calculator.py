print("Welcome to the Bill Calculator!")
total = input("What is the total bill?: ")
tip = input("How much do you want to tip?(10%, 12%, 15%): ")
split = input("How many people are splitting the bill?: ")

print(f"Each person should pay {(float(total) + ((float(tip)/100) * float(total))) / float(split):.2f}")