while True:
    namn = input("What is your name? ").strip()
    namn2 = input("Vad sade du? ").strip()

    if namn2 == namn:
        print(f"Hello, {namn}. Welcome to Python")
        break   
    else:
        print("Lär dig skriva\n")

# Orkar inte skriva git add/push
