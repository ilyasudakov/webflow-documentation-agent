# Webflow Documentation Agent

A Python-based agent for interacting with Webflow's Data API v2 to manage documentation content.

## Features

- Fetch a list of documentation items from Webflow
- Retrieve specific documentation items
- Extract and modify content within the document structure
- Update and upload modified content back to Webflow

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

# Update a documentation item
python webflow_agent.py update <item_id> --content "New content"
```

## Configuration

The agent uses the following environment variables:
- `WEBFLOW_API_TOKEN`: Your Webflow API token
- `WEBFLOW_SITE_ID`: Your Webflow site ID
- `WEBFLOW_COLLECTION_ID`: The ID of your documentation collection