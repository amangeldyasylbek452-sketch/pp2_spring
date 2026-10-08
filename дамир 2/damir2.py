def caesar(mode, text, key):
    key = key % 26

    if mode == "decrypt":
        key = -key

    result = ""

    for ch in text:
        if 'A' <= ch <= 'Z':
            result += chr((ord(ch) - 65 + key) % 26 + 65)
        elif 'a' <= ch <= 'z':
            result += chr((ord(ch) - 97 + key) % 26 + 97)
        else:
            result += ch

    return result


while True:
    print("\n1 - Шифрлау")
    print("2 - Шифрды ашу")
    print("3 - Шығу")

    choice = input("Таңдау: ")

    if choice == "3":
        print("Бағдарлама аяқталды.")
        break

    text = input("Мәтін: ")
    key = int(input("Кілт: "))

    if choice == "1":
        print("Нәтиже:", caesar("encrypt", text, key))

    elif choice == "2":
        print("Нәтиже:", caesar("decrypt", text, key))

    else:
        print("Қате таңдау!")
