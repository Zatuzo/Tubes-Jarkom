alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

def encrypt(original_text, shift_amount):
    cipher_text = ""
    
    for letter in original_text:
        if letter in alphabet:
            shifted = (alphabet.index(letter) + shift_amount) % 26
            cipher_text += alphabet[shifted]
        else:
            cipher_text += letter 
            
    return cipher_text

def decode(cipher_text, shift_amount):
    normal_text = ""
    
    for letter in cipher_text:
        if letter in alphabet:
            original = (alphabet.index(letter) - shift_amount) % 26
            normal_text += alphabet[original]
        else:
            normal_text += letter 
            
    return normal_text

print("Do you want to encrypt or decode?")
choice = input().strip().upper()

if choice == "ENCRYPT":
    original_text = input("Enter text to encrypt: ").strip().upper()
    shift_amount = int(input("Enter shift amount: ").strip())
    print("Encrypted text:", encrypt(original_text, shift_amount))
elif choice == "DECODE":
    cipher_text = input("Enter text to decode: ").strip().upper()
    shift_amount = int(input("Enter shift amount: ").strip())
    print("Decrypted text:", decode(cipher_text, shift_amount))
else:
    print("Invalid choice! Please enter 'ENCRYPT' or 'DECODE'.")
    


        
        
    