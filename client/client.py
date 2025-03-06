import xmlrpc.client
from datetime import datetime

def main():
    # Connect to the server
    server = xmlrpc.client.ServerProxy('http://localhost:8000')

    while True:
        print("\nNOTEBOOK APPLICATION")
        print("1. Add a note")
        print("2. Get notes by topic")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
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
                
        elif choice == '2':
            # Get topic from user
            topic = input("Enter topic to retrieve: ")
            
            # Call the RPC method
            notes = server.get_notes_by_topic(topic)
            
            if notes:
                print(f"\n--- Notes for '{topic}' ---")
                for i, note in enumerate(notes, 1):
                    print(f"Note {i}:")
                    print(f"  Text: {note['text']}")
                    print(f"  Timestamp: {note['timestamp']}")
                    print()
            else:
                print(f"No notes found for topic '{topic}'")
                
        elif choice == '3':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()