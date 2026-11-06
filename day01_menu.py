while(True):
    print("\n=== RTI Mitra Menu")
    print("1. About RTI Mitra")
    print("2. Sample Questions")
    print("3. Rule check (RTI reply deadline)")
    print("0. Exit")

    ch = input("Enter your choice: ")

    if ch =="1":
        print("RTI Mitra explains the RTI Act in simple language and drafts a")
        print("correct RTI application for a Maharashtra or central office, with")
        print("the right fee, the 150-word limit and the reply deadline.")
        print("General information on the RTI Act, not legal advice.")

    elif ch == "2":
        print("Sample RTI questions:")
        print("1) What is the RTI application fee in Maharashtra?")
        print("2) Within how many days must the PIO reply to an RTI?")
        print("3) Can I ask for information about my own panchayat in Marathi?")
        print("4) Draft an RTI to Kopargaon Panchayat Samiti for the 2026 road-repair work order and payment status, and tell me the first-appeal date if there is no reply.")
        print("5) What is different between filing RTI to a central ministry online and to a Maharashtra department online?")
        print("6) What did the PIO of Kopargaon municipal council reply to RTIs last month?")
    elif ch == "3":
        print("1. The PIO must reply within 30 days.")
        print("2. Via APIO, add 5 days - reply due within 35 days.")
        print("3. For life and liberty, the PIO must reply within 48 hours.")
    elif ch == "0":
        print("Goodbye from RTI Mitra")
        break
    else:
        print("Invalid Choice, Pls pick 0, 1, 2, 3. ")

