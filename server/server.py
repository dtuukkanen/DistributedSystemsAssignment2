from xmlrpc.server import SimpleXMLRPCServer
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime
import threading

# File path for the XML database
XML_FILE = "notes_database.xml"

# Lock for thread safety when accessing the XML file
file_lock = threading.Lock()

def initialize_xml_if_needed():
    """Initialize the XML file if it does not exist."""
    if not os.path.exists(XML_FILE):
        root = ET.Element("notes")
        tree = ET.ElementTree(root)
        with file_lock:
            with open(XML_FILE, "wb") as file:
                tree.write(file)
                
def add_note(topic, text, timestamp=None):
    """
    Add a note to the XML database
    
    Args:
        topic: The topic of the note
        text: The content of the note
        timestamp: Optional timestamp, defaults to current time if not provided
    
    Returns:
        True if successful, False otherwise
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    
    try:
        initialize_xml_if_needed()
        
        # Load the XML file
        with file_lock:
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            
            # Check if topic exists
            topic_element = None
            for element in root.findall('topic'):
                if element.get('name') == topic:
                    topic_element = element
                    break
            
            # If topic doesn't exist, create it
            if topic_element is None:
                topic_element = ET.SubElement(root, 'topic', name=topic)
            
            # Add the new note
            note_element = ET.SubElement(topic_element, 'note')
            
            # Add text and timestamp to the note
            text_element = ET.SubElement(note_element, 'text')
            text_element.text = text
            
            time_element = ET.SubElement(note_element, 'timestamp')
            time_element.text = timestamp
            
            # Generate XML with pretty formatting but remove empty lines
            rough_string = ET.tostring(root, encoding='utf-8')
            reparsed = minidom.parseString(rough_string)
            xmlstr = reparsed.toprettyxml(indent="  ")
            
            # Filter out lines that are just whitespace
            cleaned_xmlstr = '\n'.join([line for line in xmlstr.splitlines() if line.strip()])
            
            # Save the cleaned XML to file
            with open(XML_FILE, "w") as f:
                f.write(cleaned_xmlstr)
                
            return True
    except Exception as e:
        print(f"Error adding note: {e}")
        return False

def get_notes_by_topic(topic):
    """
    Retrieve notes by topic from the XML database
    
    Args:
        topic: The topic to search for
    
    Returns:
        A list of dictionaries containing note text and timestamps
    """
    try:
        initialize_xml_if_needed()
        
        with file_lock:
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            
            # Find the requested topic
            for topic_element in root.findall('topic'):
                if topic_element.get('name') == topic:
                    notes = []
                    
                    # Collect all notes for this topic
                    for note_element in topic_element.findall('note'):
                        text = note_element.find('text').text
                        timestamp = note_element.find('timestamp').text
                        notes.append({'text': text, 'timestamp': timestamp})
                    
                    return notes
            
            # Topic not found
            return []
    except Exception as e:
        print(f"Error retrieving notes: {e}")
        return []

def main():
    # Create a simple XML-RPC server
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    print("Listening on port 8000...")

    # Register functions
    server.register_function(add_note, "add_note")
    server.register_function(get_notes_by_topic, "get_notes_by_topic")

    # Start the server
    try: 
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down...")

if __name__ == "__main__":
    main()
