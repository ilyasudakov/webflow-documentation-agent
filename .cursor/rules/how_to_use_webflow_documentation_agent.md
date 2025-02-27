## Webflow Documentation Agent Rule

This rule contains instructions how to use Webflow integrations.

### How to Use

Simply ask Cursor AI about managing Webflow documentation using natural language. For example:

- "List all documentation items in Webflow"
- "Get documentation item with ID abc123"
- "Extract content from item xyz789"
- "Save content from item xyz789 to a file"
- "Update the title field in item abc123"

Cursor AI will suggest the appropriate command to run based on your request. 
/collection_items directory is used to collect all retrieved documents for analysis by Cursor.

### Available Commands

The rule supports the following operations:

1. **List and Save Documentation Items**
   ```
   python webflow_agent.py list --save
   python webflow_agent.py list --save --output-dir "collection_items" --filename "webflow_docs.json"
   ```

2. **Get Documentation Item**
   ```
   python webflow_agent.py get {item_id}
   ```

3. **Extract and Save Content**
   ```
   # Extract and save the full document (default behavior)
   python webflow_agent.py extract {item_id}
   
   # Extract specific content using a path (optional)
   python webflow_agent.py extract {item_id} --path content.sections.0
   
   # Specify custom output directory
   python webflow_agent.py extract {item_id} --output-dir custom_folder
   ```

4. **Update Documentation Item**
   ```
   # Update specific content using a path
   python webflow_agent.py update {item_id} --path content.sections.0 --content '{"title": "New Title"}'
   
   # Update the entire document
   python webflow_agent.py update {item_id} --content '{"title": "New Title", "content": {...}}'
   
   # Update using content from a file
   python webflow_agent.py update {item_id} --file path/to/content.json
   ```

For more details about each command, refer to the `webflow_agent.py` script or run:
```
python webflow_agent.py --help
``` 