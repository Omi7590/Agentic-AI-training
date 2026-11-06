product = ("Explains the RTI Act in simple language and drafts a correct RTI application for a Maharashtra or central office, with fee, word limit and reply deadline.")

user = ("Final-year student in Kopargaon who wants to know, through RTI, why the gram panchayat's road-repair work order is pending, and has never filed an RTI.")

problem = ("The RTI process is confusing - different rules for central vs "
           "Maharashtra, legal language is hard, and people do not know the "
           "fees, deadlines or how to draft a valid application.")

data_source = "https://rti.gov.in/ and https://rti.gov.in/Writereaddata/RTI-Act.pdf"


print("=== RTI Mitra Project Card ===")
print(f"Product: {product}")
print(f"User: {user}")
print(f"Problem: {problem}")
print(f"Data Source: {data_source}")


name = input("Enter Name: ")
question = input("Enter RTI Question: ")

print(f"\nHello {name}")
print(f"You asked: {question}")
