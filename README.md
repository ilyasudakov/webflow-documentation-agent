# Webflow Documentation Agent

A Python-based agent for interacting with Webflow's Data API v2 to manage documentation content using Cursor.

## Features

- Fetch a list of documentation items from Webflow
- Retrieve specific documentation items
- Extract and modify content within the document structure
- Update and upload modified content back to Webflow
- Save extracted content to local files for use in other contexts

## Requirements

- Python 3.8+
- Required packages listed in `requirements.txt`

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Webflow API credentials:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file with your Webflow API credentials

## Usage

```bash
# List all documentation items
python webflow_agent.py list

# Get a specific documentation item
python webflow_agent.py get <item_id>

# Extract content from a documentation item
python webflow_agent.py extract <item_id> --path "content.sections.0.text"

# Extract and save content to a file
python webflow_agent.py extract <item_id> --path "content.sections.0.text" --save

# Extract and save content to a custom directory
python webflow_agent.py extract <item_id> --path "content.sections.0.text" --save --output-dir "my_docs"

# Update a documentation item
python webflow_agent.py update <item_id> --path "content.sections.0.text" --content "New content"
```

## Programmatic Usage

You can also use the agent programmatically in your Python code:

```python
from webflow_agent import WebflowAgent

# Initialize the agent
agent = WebflowAgent(api_token, site_id, collection_id)

# Get an item
item = agent.get_item(item_id)

# Extract content
content = agent.extract_document_content(item, ["content", "sections", "0", "text"])

# Save content to a file
file_path = agent.save_content_to_file(item, content, "collection_items")
```

See `example_usage.py` for a complete example of programmatic usage.

## Configuration

The agent uses the following environment variables:
- `WEBFLOW_API_TOKEN`: Your Webflow API token
- `WEBFLOW_SITE_ID`: Your Webflow site ID
- `WEBFLOW_COLLECTION_ID`: The ID of your documentation collection

## Saved Content Files

When using the `--save` option or the `save_content_to_file()` method, content is saved to:
- Default directory: `collection_items/`
- Filename format: `{item_name}_{item_id}.json`

These files can be used as context in other applications or loaded back into memory for further processing.