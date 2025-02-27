#!/usr/bin/env python3
"""
Example Usage of Webflow Documentation Agent

This script demonstrates how to use the WebflowAgent class programmatically.
"""

import os
import json
from dotenv import load_dotenv
from webflow_agent import WebflowAgent
from rich.console import Console

# Initialize console for rich output
console = Console()

# Load environment variables
load_dotenv()

# API Configuration
API_TOKEN = os.getenv("WEBFLOW_API_TOKEN")
SITE_ID = os.getenv("WEBFLOW_SITE_ID")
COLLECTION_ID = os.getenv("WEBFLOW_COLLECTION_ID")

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
    items = agent.list_items(limit=5)  # Limit to 5 items for the example
    console.print(f"Found {len(items)} items")
    
    if not items:
        console.print("[yellow]No items found. Please check your API credentials and collection ID.[/yellow]")
        return
    
    # Example 2: Get a specific item
    console.print("\n[bold green]Example 2:[/bold green] Getting a specific documentation item")
    item_id = items[0]["id"]  # Use the first item from the list
    console.print(f"Getting item with ID: {item_id}")
    item = agent.get_item(item_id)
    console.print(f"Item name: {item.get('fieldData', {}).get('name', 'Untitled')}")
    
    # Example 3: Extract content from a specific path
    console.print("\n[bold green]Example 3:[/bold green] Extracting content from a specific path")
    # This is just an example path - you'll need to adjust based on your actual document structure
    example_path = ["content", "sections", "0", "text"] if "content" in item.get("fieldData", {}) else []
    
    if example_path:
        content = agent.extract_document_content(item, example_path)
        console.print("Extracted content:")
        console.print(json.dumps(content, indent=2) if content else "No content found at this path")
    else:
        console.print("[yellow]No suitable path found in this document for extraction example.[/yellow]")
        # Show the available top-level fields
        console.print("Available top-level fields:")
        console.print(list(item.get("fieldData", {}).keys()))
    
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