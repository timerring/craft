# MCP Servers Documentation

This document provides detailed information about each MCP (Model Context Protocol) server configured in `mcp.json`.

---

## 1. chrome-devtools

### Purpose
Browser automation and DevTools integration for web page inspection, interaction, debugging, and testing.

### Repository
- npm: `chrome-devtools-mcp`
- GitHub: https://github.com/nickgnd/chrome-devtools-mcp

### Main Tools
| Tool | Description |
|------|-------------|
| `list_pages` | List all open browser pages |
| `navigate_page` | Navigate to URL, back, forward, or reload |
| `take_screenshot` | Capture page or element screenshot |
| `take_snapshot` | Get text snapshot of page (a11y tree) |
| `click` | Click on elements |
| `fill` | Fill form inputs |
| `evaluate_script` | Execute JavaScript in page |
| `list_network_requests` | View network requests |
| `list_console_messages` | View console logs |
| `hover` | Hover over elements |
| `press_key` | Press keyboard keys |
| `drag` | Drag and drop elements |
| `upload_file` | Upload files through file inputs |
| `handle_dialog` | Handle browser dialogs |
| `emulate` | Emulate device, timezone, network conditions |
| `lighthouse_audit` | Run Lighthouse accessibility audits |
| `performance_start_trace` | Start performance profiling |
| `performance_stop_trace` | Stop performance profiling |

### Configuration
```json
{
  "command": "npx",
  "args": ["-y", "chrome-devtools-mcp@latest", "--browser-url=http://127.0.0.1:9222"]
}
```

### Requirements
- Chrome/Chromium browser running with remote debugging enabled
- Start Chrome with: `--remote-debugging-port=9222`

---

## 2. dart

### Purpose
Dart and Flutter development tooling integration for analysis, testing, app execution, and hot reload.

### Repository
- Official Dart SDK MCP Server
- GitHub: https://github.com/dart-lang/sdk/tree/main/pkg/mcp_server

### Main Tools
| Tool | Description |
|------|-------------|
| `analyze_files` | Analyze Dart/Flutter project for errors |
| `run_tests` | Run Dart/Flutter tests |
| `launch_app` | Launch Flutter app on device |
| `stop_app` | Stop running Flutter app |
| `hot_reload` | Hot reload Flutter app |
| `hot_restart` | Hot restart Flutter app |
| `get_runtime_errors` | Get runtime errors from app |
| `get_widget_tree` | Get Flutter widget tree |
| `list_devices` | List available Flutter devices |
| `get_app_logs` | Get app logs |
| `pub` | Run pub commands (get, add, upgrade, etc.) |
| `pub_dev_search` | Search pub.dev for packages |
| `dart_format` | Format Dart code |
| `dart_fix` | Apply Dart fixes |
| `create_project` | Create new Dart/Flutter project |
| `hover` | Get hover information at cursor position |
| `signature_help` | Get signature help for APIs |
| `resolve_workspace_symbol` | Look up symbols in workspace |
| `connect_dart_tooling_daemon` | Connect to Dart Tooling Daemon |

### Configuration
```json
{
  "command": "dart",
  "args": ["mcp-server"]
}
```

### Requirements
- Dart SDK installed
- Flutter SDK (for Flutter projects)

---

## 3. figma-remote-mcp-server

### Purpose
Figma design tool integration for reading designs, generating code from designs, and managing Code Connect mappings.

### Repository
- Official Figma MCP Server
- GitHub: https://github.com/figma/figma-mcp-server

### Main Tools
| Tool | Description |
|------|-------------|
| `get_design_context` | Get design context for a node (primary design-to-code tool) |
| `get_screenshot` | Get screenshot of a Figma node |
| `get_metadata` | Get metadata for a node or page |
| `get_figjam` | Generate UI code for FigJam nodes |
| `get_variable_defs` | Get variable definitions for a node |
| `get_code_connect_map` | Get Code Connect mapping for a node |
| `get_code_connect_suggestions` | Get AI-suggested Code Connect mappings |
| `send_code_connect_mappings` | Save Code Connect mappings |
| `add_code_connect_map` | Add a single Code Connect mapping |
| `create_design_system_rules` | Generate design system rules prompt |
| `generate_diagram` | Create diagrams in FigJam using Mermaid |
| `create_new_file` | Create new Figma file |
| `whoami` | Get authenticated user info |

### Configuration
```json
{
  "serverUrl": "https://mcp.figma.com/mcp"
}
```

### Requirements
- Figma account with API access
- Figma Personal Access Token configured

---

## 4. proxyman

### Purpose
HTTP/HTTPS traffic inspection and debugging for API development and network analysis.

### Repository
- Proxyman macOS Application
- Website: https://proxyman.io

### Main Tools
| Tool | Description |
|------|-------------|
| `get_flows` | Get captured HTTP/HTTPS flows |
| `get_flow_detail` | Get detailed flow information |
| `filter_flows` | Filter flows by criteria |
| `export_flow_curl` | Export flow as cURL command |
| `create_breakpoint` | Create breakpoint rule for requests/responses |
| `create_map_local` | Create map local rule (mock responses) |
| `create_map_remote` | Create map remote rule (redirect requests) |
| `create_blacklist` | Create blacklist rule (block requests) |
| `enable_ssl_proxying` | Enable SSL proxying for domain |
| `get_ssl_proxying_list` | Get SSL proxying configuration |
| `get_certificate_status` | Get root certificate status |
| `get_proxy_status` | Get proxy status |
| `toggle_recording` | Start/stop traffic recording |
| `clear_session` | Clear captured flows |
| `list_rules` | List active debugging rules |
| `open_proxyman` | Launch Proxyman app |
| `quit_proxyman` | Quit Proxyman app |
| `get_version` | Get Proxyman version |

### Configuration
```json
{
  "command": "/Applications/Proxyman.app/Contents/MacOS/mcp-server"
}
```

### Requirements
- Proxyman macOS application installed
- macOS only

---

## 5. Context7

### Purpose
External library and API documentation understanding. Provides up-to-date documentation for any library or API.

### Repository
- Upstash Context7 MCP
- GitHub: https://github.com/upstash/context7-mcp

### Main Tools
| Tool | Description |
|------|-------------|
| `resolve-library-id` | Resolve library ID from name |
| `query-docs` | Query documentation for a library |

### Configuration
```json
{
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp"],
  "env": {
    "CONTEXT7_API_KEY": "YOUR_CONTEXT7_API_KEY_HERE"
  }
}
```

### Requirements
- Context7 API key from Upstash
- Get API key at: https://context7.com

---

## 6. sequential-thinking

### Purpose
Structured thinking and reasoning for complex problems. Helps break down problems step by step.

### Repository
- Model Context Protocol Server - Sequential Thinking
- GitHub: https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking

### Main Tools
| Tool | Description |
|------|-------------|
| `sequentialthinking` | Perform sequential thinking steps |

### Configuration
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
}
```

---

## 7. mcp-server-time

### Purpose
Time and timezone utilities for scheduling and time-based operations.

### Repository
- MCP Server Time
- GitHub: https://github.com/GongRzhe/mcp-server-time

### Main Tools
| Tool | Description |
|------|-------------|
| `get_current_time` | Get current time in specified timezone |
| `convert_time` | Convert time between timezones |

### Configuration
```json
{
  "command": "uvx",
  "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"]
}
```

### Requirements
- Python uvx (uv package runner)

---

## 8. serena

### Purpose
Symbol-based code navigation and editing for Python projects. Provides IDE-like code intelligence.

### Repository
- GitHub: https://github.com/oraios/serena

### Main Tools
| Tool | Description |
|------|-------------|
| `list_dir` | List directory contents |
| `find_file` | Find files by pattern |
| `search_for_pattern` | Search for patterns in code |
| `get_symbols_overview` | Get overview of symbols in file |
| `find_symbol` | Find symbol by name |
| `find_referencing_symbols` | Find symbols referencing a symbol |
| `replace_symbol_body` | Replace symbol body |
| `insert_after_symbol` | Insert code after symbol |
| `insert_before_symbol` | Insert code before symbol |
| `rename_symbol` | Rename a symbol |
| `activate_project` | Activate a project |
| `get_current_config` | Get current configuration |
| `onboarding` | Run project onboarding |
| `write_memory` / `read_memory` / `list_memories` / `delete_memory` / `edit_memory` | Memory management |

### Configuration
```json
{
  "command": "uvx",
  "args": [
    "--from",
    "git+https://github.com/oraios/serena",
    "serena",
    "start-mcp-server",
    "--context",
    "ide-assistant"
  ]
}
```

### Requirements
- Python uvx (uv package runner)

---

## 9. morph

### Purpose
Fast code editing and codebase search with AI-powered features.

### Repository
- Morph MCP
- Website: https://morph.dev
- GitHub: https://github.com/morph-llm/morph-mcp

### Main Tools
| Tool | Description |
|------|-------------|
| `edit_file` | Fast file editing |
| `warpgrep_codebase_search` | AI-powered codebase search |

### Configuration
```json
{
  "command": "npx",
  "args": ["-y", "@morphllm/morphmcp"],
  "env": {
    "MORPH_API_KEY": "YOUR_MORPH_API_KEY_HERE",
    "ALL_TOOLS": "true"
  }
}
```

### Requirements
- Morph API key
- Get API key at: https://morph.dev

---

## 10. tavily-mcp

### Purpose
Web search and content extraction for research and information gathering.

### Repository
- Tavily MCP
- Website: https://tavily.com
- GitHub: https://github.com/tavily-ai/tavily-mcp

### Main Tools
| Tool | Description |
|------|-------------|
| `tavily_search` | Search the web |
| `tavily_extract` | Extract content from URLs |
| `tavily_crawl` | Crawl websites |
| `tavily_map` | Map website structure |
| `tavily_research` | Deep research on a topic |

### Configuration
```json
{
  "command": "npx",
  "args": ["-y", "tavily-mcp@latest"],
  "env": {
    "TAVILY_API_KEY": "YOUR_TAVILY_API_KEY_HERE",
    "DEFAULT_PARAMETERS": "{\"include_images\": true, \"max_results\": 15, \"search_depth\": \"advanced\"}"
  }
}
```

### Requirements
- Tavily API key
- Get API key at: https://tavily.com

---

## 11. pencil

### Purpose
Kiro IDE extension integration for enhanced development workflows.

### Repository
- Pencil for Kiro
- Website: https://pencil.dev

### Configuration
```json
{
  "command": "/path/to/mcp-server-darwin-arm64",
  "args": ["--app", "kiro"]
}
```

### Note
This is a local extension binary. Path varies by installation.

---

## MCP Server Categories

### Development Tools
- `dart` - Dart/Flutter development
- `serena` - Python code navigation
- `morph` - Fast code editing

### Browser & UI
- `chrome-devtools` - Browser automation
- `figma-remote-mcp-server` - Design integration

### Knowledge & Search
- `Context7` - Library documentation
- `tavily-mcp` - Web search

### Debugging & Analysis
- `proxyman` - HTTP traffic inspection

### Utilities
- `sequential-thinking` - Structured reasoning
- `mcp-server-time` - Time utilities

---

## Usage Notes

1. **API Keys**: Replace `YOUR_*_API_KEY_HERE` placeholders with actual keys
2. **Disabled**: Set `"disabled": true` to disable a server
3. **Local Paths**: Adjust paths like Proxyman or Pencil to match your installation
4. **Platform**: Some servers (like Proxyman) are macOS only