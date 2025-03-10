from xmlrpc.server import SimpleXMLRPCServer
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime
import threading
import requests

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


def communicate_with_wikipedia(search_term):
    # Create a session
    S = requests.Session()

    # Set url
    URL = "https://en.wikipedia.org/w/api.php"

    # Set parameters
    PARAMS = {
        "action": "opensearch",
        "namespace": 0,
        "search": search_term,
        "limit": 1,
        "format": "json"
    }

    # Send GET request and save the response as R
    R = S.get(url=URL, params=PARAMS)

    # Convert response to JSON
    DATA = R.json()

    results = {
        "title": DATA[1][0],
        "description": DATA[2][0], # This is empty string because the API is restricted by Wikipedia
        "url": DATA[3][0]
    }

    print(results)
    return results


def add_wikipedia_search_results_to_xml(search_term, results):
    """
    Add Wikipedia URL to an existing topic in the XML database
    Args:
        search_term: The term used for the Wikipedia search (should match a topic name)
        results: The results from the Wikipedia search
    """
    try:
        initialize_xml_if_needed()
        
        with file_lock:
            tree = ET.parse(XML_FILE)
            root = tree.getroot()
            
            # Find the matching topic
            topic_found = False
            for topic_element in root.findall('topic'):
                if topic_element.get('name') == search_term:
                    # Check if this topic already has a Wikipedia URL
                    existing_wiki = topic_element.find('wikipedia_url')
                    if existing_wiki is not None:
                        print(f"Wikipedia URL already exists for topic '{search_term}'")
                        return False
                    
                    # Add Wikipedia information to the existing topic
                    wikipedia_element = ET.SubElement(topic_element, 'wikipedia_url')
                    wikipedia_element.text = results['url']
                    
                    # Optionally add title and description as attributes
                    wikipedia_element.set('title', results['title'])
                    
                    topic_found = True
                    break
            
            if not topic_found:
                print(f"Topic '{search_term}' not found, Wikipedia info not added")
                return False
            
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
        print(f"Error adding Wikipedia search results: {e}")
        return False


def lookup_wikipedia(search_term):
    """
    Lookup data on Wikipedia and add it to the corresponding topic
    
    Args:
        search_term: The term to search for on Wikipedia (should match a topic name)
    
    Returns:
        True if successful, False otherwise
    """
    results = communicate_with_wikipedia(search_term)
    return add_wikipedia_search_results_to_xml(search_term, results)


def main():
    # Create a simple XML-RPC server
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    print("Listening on port 8000...")

    # Register functions
    server.register_function(add_note, "add_note")
    server.register_function(lookup_wikipedia, "lookup_wikipedia")

    # Start the server
    try: 
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server shutting down...")

if __name__ == "__main__":
    main()
