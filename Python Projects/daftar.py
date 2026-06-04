daftar = []

def menu():
    print("\n1. Tambah aktifitas")
    print("2. Hapus aktifitas")
    print("3. Tunjukkan aktifitas yang sudah ada")
    print("4. Keluar dari Menu")

def Tunjukkan_daftar():
    if len(daftar) > 0:
        print("\nIsi List kamu:")
        for index, aktifitas in enumerate(daftar):
            print(f"{index}. {aktifitas}")
    else:
        print("\nList kamu kosong!")

def Tambah_list():
    aktifitas = input("Masukkan aktifitas yang ingin dimasukkan: ")
    daftar.append(aktifitas)
    print(f"Aktivitas '{aktifitas}' telah dimasukkan ke dalam daftar!")

def Hapus_daftar():
    if len(daftar) == 0:
        print("\nList kamu kosong! Tidak ada yang bisa dihapus.")
        return

    Tunjukkan_daftar()
    try:
        Hapus = int(input("Pilih Nomor aktifitas yang ingin dihapus: "))
        daftar_terhapus = daftar.pop(Hapus)
        print(f"Aktivitas '{daftar_terhapus}' telah dihapus!")
    except (IndexError, ValueError):
        print("Nomor yang dimasukkan tidak valid.")

while True:
    menu()
    pilihan = input("Pilihlah Hal yang ingin dilakukan: ")

    if pilihan == "1":
        Tambah_list()
    elif pilihan == "2":
        Hapus_daftar()
    elif pilihan == "3":
        Tunjukkan_daftar()
    elif pilihan == "4":
        print("Telah keluar dari program daftar.")
        break
    else:
        print("Pilihan tidak sesuai. Silakan coba lagi!")
