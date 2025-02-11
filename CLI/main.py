import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Tasks import cleanup, compression, email, conversion, scraping
def show_menu():
    print("Select a task to run:")
    print("1. File Cleanup")
    print("2. File Compression")
    print("3. Email Automation")
    print("4. File Conversion")
    print("5. Data Scraping")
    print("6. Exit")

def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            cleanup.run_cleanup()
        elif choice == '2':
            compression.run_compression()
        elif choice == '3':
            email.run_email_automation()
        elif choice == '4':
            conversion.run_conversion()
        elif choice == '5':
            scraping.run_scraping()
        elif choice == '6':
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid choice. Please try again.")

        # After completing a task, ask if the user wants to return to the main menu or exit
        next_action = input("Do you want to return to the main menu? (yes/no): ").lower()
        if next_action != 'yes':
            print("Exiting...")
            sys.exit()

if __name__ == "__main__":
    main()