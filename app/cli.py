#   RTI Mitra = CLI entry point
# uses app/records.py to load, search and count RTI rule Records.

from app.records import load_records, search, count_by, get_by_id

def print_record (i, r):
    print(f"\n{i}. [{r['jurisdiction']}] {r['topic']}")
    print(f"   Rule   : {r['rule']}")
    print(f"   Ref    : {r['section_or_rule_ref']}")
    print(f"   Limit  : {r['amount_or_time_limit']}")
    print(f"   Source : {r['source_url']}")

def main ():
    while True:
        print("\n=== RTI Mitra - Record Explorer ===")
        print("1. Show all records")
        print("2. Search by keyword")
        print("3. Count by jurisdiction")
        print("4. Get record by ID")
        print("0. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            records = load_records()
            print(f"\nTotal records: {len(records)}")
            for i, r in enumerate(records, 1):
                print_record(i, r)

        elif choice == "2":
            keyword = input("Enter keyword: ").strip()
            results = search(keyword)
            if results:
                print(f"\n{len(results)} result(s) for '{keyword}':")
                for i, r in enumerate(results, 1):
                    print_record(i, r)
            else:
                print(f"No records found for '{keyword}'.")

        elif choice == "3":
            counts = count_by("jurisdiction")
            print("\nRecords by jurisdiction:")
            for cat, count in counts.items():
                print(f"  {cat}: {count}")

        elif choice == "4":
            try:
                index = int(input("Enter record number (1-based): ").strip()) - 1
                r = get_by_id(index)
                if r:
                    print_record(index + 1, r)
                else:
                    print("No record found at that ID.")
            except ValueError:
                print("Please enter a valid number.")

        elif choice == "0":
            print("Goodbye from RTI Mitra!")
            break

        else:
            print("Invalid choice. Pick 0-4.")

if __name__ == "__main__":
    main()