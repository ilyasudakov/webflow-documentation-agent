# Cursor Rules for Webflow Documentation Agent

This directory contains custom rules for Cursor AI to help you interact with the Webflow Documentation Agent.

## Webflow Documentation Agent Rule

The `webflow_docs_agent.json` rule enables Cursor AI to assist you with managing documentation content in Webflow using the `webflow_agent.py` script.

### Prerequisites

Before using this rule, make sure you have:

1. Set up your environment variables in a `.env` file:
   - `WEBFLOW_API_TOKEN`
   - `WEBFLOW_SITE_ID`
   - `WEBFLOW_COLLECTION_ID`

2. Installed the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### How to Use

Simply ask Cursor AI about managing Webflow documentation using natural language. For example:

- "List all documentation items in Webflow"
- "Get documentation item with ID abc123"
- "Extract content from item xyz789 at path content.sections.0"
- "Save content from item xyz789 to a file"
- "Update the title field in item abc123"

Cursor AI will suggest the appropriate command to run based on your request.

### Available Commands

The rule supports the following operations:

1. **List Documentation Items**
   ```
   python webflow_agent.py list
   ```

2. **Get Documentation Item**
   ```
   python webflow_agent.py get {item_id}
   ```

3. **Extract Content**
   ```
   python webflow_agent.py extract {item_id} --path {path}
   ```

4. **Save Extracted Content**
   ```
   python webflow_agent.py extract {item_id} --path {path} --save --output-dir collection_items
   ```

5. **Update Documentation Item**
   ```
   python webflow_agent.py update {item_id} --path {path} --content '{json_content}'
   ```

For more details about each command, refer to the `webflow_agent.py` script or run:
```
python webflow_agent.py --help
``` 