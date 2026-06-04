import random

words = ["CHICKEN", "COW", "SHEEP", "DEER", "ELEPHANT", "ARMADILLO"]

random_word = random.choice(words)

guessed_word = ["_"] * len(random_word)

blanks = list(random_word)

attempts = 6

guessed_letters = set()

while attempts > 0 and "_" in guessed_word:
    print("\n" + " ".join(guessed_word))  
    guessed = input("Guess a letter: ").upper()

    if len(guessed) != 1 or not guessed.isalpha():
        print("Masukkan satu huruf!")
        continue

    if guessed in guessed_letters:
        print("Kamu sudah menebak huruf ini!")
        continue

    guessed_letters.add(guessed) 


    if guessed in blanks:
        for i in range(len(random_word)):
            if blanks[i] == guessed:
                guessed_word[i] = guessed
        print("Benar!")
    else:
        attempts -= 1
        print(f"Salah! Sisa percobaan: {attempts}")

if "_" not in guessed_word:
    print("\nSelamat! Kamu berhasil menebak kata:", random_word)
else:
    print("\nKamu kalah! Kata yang benar adalah:", random_word)
