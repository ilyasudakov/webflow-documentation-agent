#!/usr/bin/env python3
"""
Webflow Documentation Agent

A script to interact with Webflow's Data API v2 for managing documentation content.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path

# Initialize console for rich output
console = Console()

# Load environment variables
load_dotenv()

# API Configuration
API_TOKEN = os.getenv("WEBFLOW_API_TOKEN")
SITE_ID = os.getenv("WEBFLOW_SITE_ID")
COLLECTION_ID = os.getenv("WEBFLOW_COLLECTION_ID")
API_BASE_URL = "https://api.webflow.com/v2"

class WebflowAgent:
    """Agent for interacting with Webflow Data API v2."""
    
    def __init__(self, token: str, site_id: str, collection_id: str):
        """Initialize the Webflow agent with API credentials."""
        self.token = token
        self.site_id = site_id
        self.collection_id = collection_id
        self.headers = {
            "Authorization": f"Bearer {self.token}",
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
        """
        Get a list of items from the collection.
        
        This method handles pagination automatically and retrieves all items
        by making multiple requests if necessary.
        
        Args:
            limit (int): Maximum number of items to retrieve per request (max 100)
            
        Returns:
            List[Dict]: A list of all items in the collection
        """
        all_items = []
        offset = 0
        total_items = None
        
        while total_items is None or offset < total_items:
            endpoint = f"/collections/{self.collection_id}/items?limit={limit}&offset={offset}"
            response = self._make_request("get", endpoint)
            
            # Get items from the current page
            items = response.get("items", [])
            all_items.extend(items)
            
            # Get pagination info
            pagination = response.get("pagination", {})
            total_items = pagination.get("total", 0)
            
            # If we got fewer items than the limit, we've reached the end
            if len(items) < limit:
                break
                
            # Update offset for the next request
            offset += limit
            
            # Provide feedback during retrieval of large collections
            console.print(f"[bold blue]Retrieved {len(all_items)} of {total_items} items...[/bold blue]")
        
        return all_items
    
    def get_item(self, item_id: str) -> Dict:
        """
        Get a specific item by ID.
        
        Args:
            item_id (str): ID of the item to retrieve
            
        Returns:
            Dict: Item data
        """
        endpoint = f"/collections/{self.collection_id}/items/{item_id}"
        return self._make_request("get", endpoint)
    
    def update_item(self, item_id: str, data: Dict) -> Dict:
        """
        Update a specific item.
        
        Args:
            item_id (str): ID of the item to update
            data (Dict): Data to update, should contain fieldData and/or isArchived, isDraft
            
        Returns:
            Dict: Updated item data
        """
        endpoint = f"/collections/{self.collection_id}/items/{item_id}"
        
        # Ensure data has the correct structure according to the API documentation
        update_data = {}
        if "fieldData" in data:
            update_data["fieldData"] = data["fieldData"]
        if "isArchived" in data:
            update_data["isArchived"] = data["isArchived"]
        if "isDraft" in data:
            update_data["isDraft"] = data["isDraft"]
        if "cmsLocaleId" in data:
            update_data["cmsLocaleId"] = data["cmsLocaleId"]
            
        return self._make_request("patch", endpoint, update_data)
    
    def save_content_to_file(self, item: Dict, content: Any, base_dir: str = "collection_items") -> str:
        """
        Save the extracted content to a file in the specified directory.
        
        Args:
            item (Dict): The item metadata containing id and name
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
        
    def save_items_list(self, items: List[Dict], base_dir: str = "collection_items", filename: str = "all_items.json") -> str:
        """
        Save the full list of documentation items to a file for easier searching.
        
        Args:
            items (List[Dict]): List of documentation items
            base_dir (str): Base directory to save the file
            filename (str): Name of the file to save the list
            
        Returns:
            str: Path to the saved file
        """
        # Create the directory if it doesn't exist
        Path(base_dir).mkdir(exist_ok=True)
        
        # Create a simplified version of the items with essential information for searching
        simplified_items = []
        for item in items:
            simplified_item = {
                "id": item.get("id", ""),
                "name": item.get("fieldData", {}).get("name", "Untitled"),
                "lastUpdated": item.get("lastUpdated", ""),
                "createdOn": item.get("createdOn", ""),
                "slug": item.get("fieldData", {}).get("slug", ""),
                # Add any other fields that would be useful for searching
            }
            simplified_items.append(simplified_item)
        
        # Save the simplified items to the file
        file_path = os.path.join(base_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(simplified_items, f, indent=2)
        
        console.print(f"[bold green]Items list saved to:[/bold green] {file_path}")
        return file_path


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


def main():
    """Main CLI function for the Webflow Documentation Agent."""
    import argparse
    
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Webflow Documentation Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all documentation items")
    list_parser.add_argument("--save", action="store_true", help="Save the list to a file")
    list_parser.add_argument("--output-dir", default="collection_items", help="Directory to save output files")
    list_parser.add_argument("--filename", default="all_items.json", help="Filename for the saved list")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a specific documentation item")
    get_parser.add_argument("item_id", help="ID of the item to get")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract content from a documentation item")
    extract_parser.add_argument("item_id", help="ID of the item to extract content from")
    extract_parser.add_argument("--save", action="store_true", help="Save the extracted content to a file")
    extract_parser.add_argument("--output-dir", default="collection_items", help="Directory to save output files")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a documentation item")
    update_parser.add_argument("item_id", help="ID of the item to update")
    update_parser.add_argument("--field-data", help="JSON string of field data to update")
    update_parser.add_argument("--is-archived", type=bool, help="Set item archived status")
    update_parser.add_argument("--is-draft", type=bool, help="Set item draft status")
    update_parser.add_argument("--cms-locale-id", help="CMS locale ID for the item")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check for required environment variables
    if not all([API_TOKEN, SITE_ID, COLLECTION_ID]):
        console.print("[bold red]Error:[/bold red] Missing required environment variables.")
        console.print("Please set WEBFLOW_API_TOKEN, WEBFLOW_SITE_ID, and WEBFLOW_COLLECTION_ID.")
        console.print("You can create a .env file based on the .env.example template.")
        return
    
    # Initialize the agent
    agent = WebflowAgent(API_TOKEN, SITE_ID, COLLECTION_ID)
    
    # Execute the command
    if args.command == "list":
        console.print("[bold blue]Listing documentation items...[/bold blue]")
        items = agent.list_items()
        display_items(items)
        
        if args.save:
            file_path = agent.save_items_list(items, args.output_dir, args.filename)
            console.print(f"[bold green]Items list saved to:[/bold green] {file_path}")
    
    elif args.command == "get":
        console.print(f"[bold blue]Getting documentation item with ID: {args.item_id}[/bold blue]")
        item = agent.get_item(args.item_id)
        display_item(item)
    
    elif args.command == "extract":
        console.print(f"[bold blue]Extracting content from item with ID: {args.item_id}[/bold blue]")
        item = agent.get_item(args.item_id)
        content = item.get("fieldData", {})
        
        console.print("[bold]Extracted content:[/bold]")
        if isinstance(content, (dict, list)):
            console.print(json.dumps(content, indent=2))
        else:
            console.print(str(content))
        
        if args.save:
            file_path = agent.save_content_to_file(item, content, args.output_dir)
            console.print(f"[bold green]Content saved to:[/bold green] {file_path}")
    
    elif args.command == "update":
        console.print(f"[bold blue]Updating content in item with ID: {args.item_id}[/bold blue]")
        
        # Create update data structure
        update_data = {}
        
        # Parse the field-data argument if provided
        if args.field_data:
            try:
                update_data["fieldData"] = json.loads(args.field_data)
            except json.JSONDecodeError:
                console.print("[bold red]Error:[/bold red] Invalid JSON in field-data")
                return
        
        # Add other update parameters if provided
        if args.is_archived is not None:
            update_data["isArchived"] = args.is_archived
        
        if args.is_draft is not None:
            update_data["isDraft"] = args.is_draft
            
        if args.cms_locale_id:
            update_data["cmsLocaleId"] = args.cms_locale_id
        
        # Ensure we have something to update
        if not update_data:
            console.print("[bold red]Error:[/bold red] No update data provided")
            return
            
        result = agent.update_item(args.item_id, update_data)
        
        console.print("[bold green]Item updated successfully![/bold green]")
        console.print(f"Updated at: {result.get('lastUpdated', 'Unknown')}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()