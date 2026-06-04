def calculate_love_score(name1, name2):
    name1 = name1.upper()
    name2 = name2.upper()  

    T, R, U, E, L, O, V = 0, 0, 0, 0, 0, 0, 0
    T += name1.count("T") + name2.count("T")
    R += name1.count("R") + name2.count("R")
    U += name1.count("U") + name2.count("U")
    E += name1.count("E") + name2.count("E")
    L += name1.count("L") + name2.count("L")
    O += name1.count("O") + name2.count("O")
    V += name1.count("V") + name2.count("V")

    total1 = (T + R + U + E) * 10
    total2 = L + O + V + E

    return total1 + total2

name1, name2 = input("").split()

print(calculate_love_score(name1, name2))
