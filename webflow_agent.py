#!/usr/bin/env python3
"""
Webflow Documentation Agent

A script to interact with Webflow's Data API v2 for managing documentation content.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Initialize console for rich output
console = Console()

# Load environment variables
load_dotenv()

# API Configuration
API_TOKEN = os.getenv("WEBFLOW_API_TOKEN")
SITE_ID = os.getenv("WEBFLOW_SITE_ID")
COLLECTION_ID = os.getenv("WEBFLOW_COLLECTION_ID")
API_BASE_URL = "https://api.webflow.com"
API_VERSION = "2.0.0"  # Webflow Data API v2

class WebflowAgent:
    """Agent for interacting with Webflow Data API v2."""
    
    def __init__(self, token: str, site_id: str, collection_id: str):
        """Initialize the Webflow agent with API credentials."""
        self.token = token
        self.site_id = site_id
        self.collection_id = collection_id
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept-Version": API_VERSION,
            "Content-Type": "application/json"
        }
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make a request to the Webflow API."""
        url = f"{API_BASE_URL}{endpoint}"
        
        try:
            if method.lower() == "get":
                response = requests.get(url, headers=self.headers)
            elif method.lower() == "post":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.lower() == "patch":
                response = requests.patch(url, headers=self.headers, json=data)
            elif method.lower() == "delete":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]Error making request:[/bold red] {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                console.print(f"Response: {e.response.text}")
            sys.exit(1)
    
    def list_items(self, limit: int = 100) -> List[Dict]:
        """Get a list of items from the collection."""
        endpoint = f"/sites/{self.site_id}/collections/{self.collection_id}/items?limit={limit}"
        response = self._make_request("get", endpoint)
        return response.get("items", [])
    
    def get_item(self, item_id: str) -> Dict:
        """Get a specific item by ID."""
        endpoint = f"/sites/{self.site_id}/collections/{self.collection_id}/items/{item_id}"
        return self._make_request("get", endpoint)
    
    def update_item(self, item_id: str, data: Dict) -> Dict:
        """Update a specific item."""
        endpoint = f"/sites/{self.site_id}/collections/{self.collection_id}/items/{item_id}"
        return self._make_request("patch", endpoint, data)
    
    def extract_document_content(self, item: Dict, cursor_path: Optional[List[str]] = None) -> Any:
        """
        Extract content at a specific cursor path within the document structure.
        If cursor_path is None, returns the entire document.
        """
        if not cursor_path:
            return item.get("fieldData", {})
        
        content = item.get("fieldData", {})
        for key in cursor_path:
            if key in content:
                content = content[key]
            else:
                console.print(f"[bold yellow]Warning:[/bold yellow] Path '{key}' not found in document")
                return None
        
        return content
    
    def update_document_content(self, item: Dict, cursor_path: List[str], new_content: Any) -> Dict:
        """
        Update content at a specific cursor path within the document structure.
        Returns the updated item data ready for submission.
        """
        # Create a copy of the original field data
        updated_data = item.get("fieldData", {}).copy()
        
        # Navigate to the correct position
        current = updated_data
        for i, key in enumerate(cursor_path[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Update the content at the final position
        if cursor_path:
            current[cursor_path[-1]] = new_content
        
        # Return the data structure for the update
        return {"fieldData": updated_data}


def display_items(items: List[Dict]) -> None:
    """Display a list of items in a formatted table."""
    if not items:
        console.print("[yellow]No items found.[/yellow]")
        return
    
    table = Table(title="Documentation Items")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Last Updated", style="magenta")
    
    for item in items:
        table.add_row(
            item.get("id", "N/A"),
            item.get("fieldData", {}).get("name", "Untitled"),
            item.get("lastUpdated", "Unknown")
        )
    
    console.print(table)


def display_item(item: Dict) -> None:
    """Display a single item's details."""
    console.print(Panel.fit(
        f"[bold cyan]ID:[/bold cyan] {item.get('id')}\n"
        f"[bold cyan]Name:[/bold cyan] {item.get('fieldData', {}).get('name', 'Untitled')}\n"
        f"[bold cyan]Last Updated:[/bold cyan] {item.get('lastUpdated', 'Unknown')}\n"
        f"[bold cyan]Created On:[/bold cyan] {item.get('createdOn', 'Unknown')}\n"
        f"[bold cyan]Published:[/bold cyan] {item.get('isArchived', False)}\n",
        title="Item Details"
    ))
    
    # Display field data in a more readable format
    console.print("[bold]Field Data:[/bold]")
    console.print(json.dumps(item.get("fieldData", {}), indent=2))


def parse_cursor_path(path_str: str) -> List[str]:
    """Parse a dot-notation path string into a list of keys."""
    if not path_str:
        return []
    return path_str.split(".")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Webflow Documentation Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List documentation items")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum number of items to retrieve")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a specific documentation item")
    get_parser.add_argument("item_id", help="ID of the item to retrieve")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract content from a documentation item")
    extract_parser.add_argument("item_id", help="ID of the item to extract from")
    extract_parser.add_argument("--path", help="Dot-notation path to the content (e.g., 'content.sections.0.text')")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a documentation item")
    update_parser.add_argument("item_id", help="ID of the item to update")
    update_parser.add_argument("--path", required=True, help="Dot-notation path to the content to update")
    update_parser.add_argument("--content", required=True, help="New content (JSON string)")
    
    args = parser.parse_args()
    
    # Check for required environment variables
    if not all([API_TOKEN, SITE_ID, COLLECTION_ID]):
        console.print("[bold red]Error:[/bold red] Missing required environment variables.")
        console.print("Please set WEBFLOW_API_TOKEN, WEBFLOW_SITE_ID, and WEBFLOW_COLLECTION_ID.")
        console.print("You can create a .env file based on the .env.example template.")
        sys.exit(1)
    
    # Initialize the agent
    agent = WebflowAgent(API_TOKEN, SITE_ID, COLLECTION_ID)
    
    # Execute the requested command
    if args.command == "list":
        items = agent.list_items(limit=args.limit)
        display_items(items)
    
    elif args.command == "get":
        item = agent.get_item(args.item_id)
        display_item(item)
    
    elif args.command == "extract":
        item = agent.get_item(args.item_id)
        cursor_path = parse_cursor_path(args.path) if args.path else None
        content = agent.extract_document_content(item, cursor_path)
        console.print(json.dumps(content, indent=2))
    
    elif args.command == "update":
        # First get the current item
        item = agent.get_item(args.item_id)
        
        # Parse the cursor path and content
        cursor_path = parse_cursor_path(args.path)
        try:
            new_content = json.loads(args.content)
        except json.JSONDecodeError:
            # If not valid JSON, treat as a string
            new_content = args.content
        
        # Update the content
        updated_data = agent.update_document_content(item, cursor_path, new_content)
        
        # Confirm with the user
        console.print("[bold yellow]About to update the following content:[/bold yellow]")
        console.print(json.dumps(updated_data, indent=2))
        confirm = input("Proceed with update? (y/n): ")
        
        if confirm.lower() == 'y':
            result = agent.update_item(args.item_id, updated_data)
            console.print("[bold green]Update successful![/bold green]")
            display_item(result)
        else:
            console.print("[yellow]Update cancelled.[/yellow]")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 