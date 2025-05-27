#!/usr/bin/env python3
"""Inspect RSS feed structure to find date elements."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import requests
import xml.etree.ElementTree as ET
from utils.logger import logger

def inspect_feed_structure():
    """Inspect the actual XML structure of a feed."""
    
    feed_url = "https://www.bing.com/news/search?q=Product+management&format=rss"
    
    try:
        response = requests.get(feed_url, timeout=30)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Find first item
        items = root.findall('.//item')
        if items:
            first_item = items[0]
            print("First RSS item structure:")
            print("=" * 50)
            
            # Print all child elements
            for child in first_item:
                print(f"Tag: {child.tag}")
                if child.text:
                    text = child.text.strip()[:100] + "..." if len(child.text.strip()) > 100 else child.text.strip()
                    print(f"Text: {text}")
                if child.attrib:
                    print(f"Attributes: {child.attrib}")
                print("-" * 30)
                
            # Check for any date-related attributes or text
            print("\nLooking for date-related content...")
            for child in first_item:
                if any(keyword in child.tag.lower() for keyword in ['date', 'time', 'published', 'pub']):
                    print(f"Potential date field: {child.tag} = {child.text}")
                    
        else:
            print("No RSS items found in feed")
            
    except Exception as e:
        print(f"Error inspecting feed: {e}")

if __name__ == "__main__":
    inspect_feed_structure()
