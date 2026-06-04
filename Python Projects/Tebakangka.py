import random

angka_benar = random.choice(range(1, 100))

for i in range(5):
    Angka_tebakan = int(input("Masukkan angka antara 1-100: "))

    if Angka_tebakan < angka_benar:
        print("Terlalu rendah Nilainya!")
    elif Angka_tebakan > angka_benar:
        print("Terlalu tinggi Nilainya!")
    elif Angka_tebakan > 100 or Angka_tebakan < 1:
            print("Nilainya di luar angka tebakan! Masukkan angka antara 1-100.")
    else:
        print(f"Benar!! Nilainya Adalah ", Angka_tebakan)
        break
else:
    print(f"Maaf, kesempatan Anda habis. Angka yang benar adalah {angka_benar}")
