#!/usr/bin/env python3
"""
Example Usage of Webflow Documentation Agent

This script demonstrates how to use the WebflowAgent class programmatically.
"""

import os
import json
from dotenv import load_dotenv
from webflow_agent import WebflowAgent
from webflow_agent import API_BASE_URL
from rich.console import Console
from pathlib import Path

# Initialize console for rich output
console = Console()

# Load environment variables
load_dotenv()

# API Configuration
API_TOKEN = os.getenv("WEBFLOW_API_TOKEN")
SITE_ID = os.getenv("WEBFLOW_SITE_ID")
COLLECTION_ID = os.getenv("WEBFLOW_COLLECTION_ID")

def save_content_to_file(item, content, base_dir="collection_items"):
    """
    Save the extracted content to a file in the specified directory.
    
    Args:
        item (dict): The item metadata containing id and name
        content (Any): The content to save
        base_dir (str): Base directory to save the files
    
    Returns:
        str: Path to the saved file
    """
    # Create the directory if it doesn't exist
    Path(base_dir).mkdir(exist_ok=True)
    
    # Get item details for filename
    item_id = item.get("id", "unknown")
    item_name = item.get("fieldData", {}).get("name", "untitled").replace(" ", "_").lower()
    
    # Create a filename based on item details
    filename = f"{item_name}_{item_id}.json"
    file_path = os.path.join(base_dir, filename)
    
    # Save the content to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        if isinstance(content, (dict, list)):
            json.dump(content, f, indent=2)
        else:
            f.write(str(content))
    
    console.print(f"[bold green]Content saved to:[/bold green] {file_path}")
    return file_path

def main():
    """Main example function."""
    # Check for required environment variables
    if not all([API_TOKEN, SITE_ID, COLLECTION_ID]):
        console.print("[bold red]Error:[/bold red] Missing required environment variables.")
        console.print("Please set WEBFLOW_API_TOKEN, WEBFLOW_SITE_ID, and WEBFLOW_COLLECTION_ID.")
        console.print("You can create a .env file based on the .env.example template.")
        return
    
    # Initialize the agent
    agent = WebflowAgent(API_TOKEN, SITE_ID, COLLECTION_ID)
    
    # Example 1: List all documentation items
    console.print("\n[bold green]Example 1:[/bold green] Listing all documentation items")
    items = agent.list_items(limit=10)  # Limit to 10 items for the example
    console.print(f"Found {len(items)} items")
    console.print(items)
    
    if not items:
        console.print("[yellow]No items found. Please check your API credentials and collection ID.[/yellow]")
        return
    
    # Example 2: Get a specific item
    console.print("\n[bold green]Example 2:[/bold green] Getting a specific documentation item using direct request")
    item_id = items[0]["id"]  # Use the first item from the list
    console.print(f"Getting item with ID: {item_id}")
    console.print("Using direct request approach instead of abstracted method")
    item = agent.get_item(item_id)
    console.print(f"Item name: {item.get('fieldData', {}).get('name', 'Untitled')}")
    console.print(f"Request URL: {API_BASE_URL}/sites/{SITE_ID}/collections/{COLLECTION_ID}/items/{item_id}")
    console.print("Request Headers:")
    console.print(json.dumps({"Authorization": "Bearer [TOKEN HIDDEN]", "Content-Type": "application/json"}, indent=2))
    
    # Example 3: Extract content from a specific path
    console.print("\n[bold green]Example 3:[/bold green] Extracting content from a specific path")
    # This is just an example path - you'll need to adjust based on your actual document structure
    example_path = ["content", "sections", "0", "text"] if "content" in item.get("fieldData", {}) else []
    
    if example_path:
        content = agent.extract_document_content(item, example_path)
        console.print("Extracted content:")
        console.print(json.dumps(content, indent=2) if content else "No content found at this path")
        
        # Save the extracted content to a file
        if content:
            file_path = save_content_to_file(item, content)
            console.print(f"[bold blue]Content saved for later use in Cursor context[/bold blue]")
    else:
        console.print("[yellow]No suitable path found in this document for extraction example.[/yellow]")
        # Show the available top-level fields
        console.print("Available top-level fields:")
        console.print(list(item.get("fieldData", {}).keys()))
        
        # Save the entire fieldData as fallback
        field_data = item.get("fieldData", {})
        if field_data:
            file_path = save_content_to_file(item, field_data)
            console.print(f"[bold blue]Full field data saved instead for later use in Cursor context[/bold blue]")
    
    # Example 4: Update content (simulation only)
    console.print("\n[bold green]Example 4:[/bold green] Updating content (simulation only)")
    # For safety, we'll just simulate the update without actually sending it
    if example_path:
        new_content = "This is updated content from the example script"
        updated_data = agent.update_document_content(item, example_path, new_content)
        console.print("Data that would be sent in an update:")
        console.print(json.dumps(updated_data, indent=2))
        console.print("[yellow]Update not actually performed in this example.[/yellow]")
    else:
        console.print("[yellow]Skipping update example as no suitable path was found.[/yellow]")
    
    console.print("\n[bold green]Example complete![/bold green]")
    console.print("To perform actual updates, use the CLI tool or modify this script.")

if __name__ == "__main__":
    main() 