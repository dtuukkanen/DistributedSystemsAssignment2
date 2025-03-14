import xmlrpc.client
from datetime import datetime

def main():
    # Connect to the server
    server = xmlrpc.client.ServerProxy('http://localhost:8000')

    while True:
        print("\nNOTEBOOK APPLICATION")
        print("1. Add a note")
        print("2. Lookup data on Wikipedia")
        print("0. Exit")
        
        choice = input("Enter your choice (0-2): ")
        
        # Add a note
        if choice == '1':
            # Get note details from user
            topic = input("Enter topic: ")
            text = input("Enter note text: ")
            timestamp = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
            
            # Call the RPC method
            success = server.add_note(topic, text, timestamp)
            
            if success:
                print("Note added successfully!")
            else:
                print("Failed to add note.")

        # Wikipedia search
        elif choice == '2':
            # Get search term from user
            search_term = input("Enter search term for Wikipedia: ")
            
            # Call the RPC method
            result = server.lookup_wikipedia(search_term)
            
            if result:
                print("Added Wikipedia information to XML successfully.")
            else:
                print("Failed to add Wikipedia information to XML.")

        # Exit the application        
        elif choice == '0':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()