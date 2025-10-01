# Research Notes: Claude CLI Integration

## Claude MCP (Model Context Protocol) Investigation

### MCP Architecture
Claude CLI uses the Model Context Protocol (MCP) for tool integration. Key findings:

1. **Protocol Type**: JSON-RPC over stdio (standard input/output)
2. **Communication**: Bidirectional, request-response pattern
3. **Tool Registration**: Static manifest-based, loaded at startup
4. **Async Support**: Required - all handlers must be async

### Claude CLI Tool Requirements

**Manifest Structure** (`~/.claude/mcp/triz-copilot.json`):
```json
{
  "name": "triz-copilot",
  "version": "1.0.0",
  "description": "TRIZ Engineering Co-Pilot",
  "server": {
    "command": "python",
    "args": ["-m", "triz_claude_mcp"],
    "env": {
      "PYTHONPATH": "/path/to/src"
    }
  },
  "tools": [
    {
      "name": "triz-workflow",
      "description": "Start guided TRIZ workflow",
      "inputSchema": {
        "type": "object",
        "properties": {}
      }
    }
  ]
}
```

### Python MCP Server Implementation

**Required Package**: `anthropic-mcp` (unofficial) or custom implementation

**Basic Server Structure**:
```python
import asyncio
import json
import sys

class MCPServer:
    async def handle_request(self, request):
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "tools/list":
            return self.list_tools()
        elif method == "tools/call":
            return await self.call_tool(params)
```

### Key Technical Considerations

1. **Async/Sync Bridge**
   - TRIZ core library is synchronous
   - MCP requires async handlers
   - Solution: Use `asyncio.to_thread()` for CPU-bound operations

2. **Session Persistence**
   - Claude doesn't maintain state between invocations
   - Must use file-based session storage
   - Session ID must be returned to user for continuity

3. **Command Parsing**
   - Claude sends raw text commands
   - Need robust regex parsing
   - Must handle variations and typos gracefully

4. **Error Handling**
   - MCP expects specific error format
   - Must not crash the server on errors
   - Graceful degradation required

## Gemini MCP Comparison

| Feature | Claude MCP | Gemini MCP |
|---------|------------|------------|
| Protocol | JSON-RPC/stdio | JSON-RPC/HTTP |
| Registration | Static manifest | Dynamic |
| Async | Required | Optional |
| State | Stateless | Stateless |
| Error Format | JSON-RPC 2.0 | Custom |
| Streaming | Not supported | Supported |

## Performance Benchmarks

### Expected Response Times

Based on existing Gemini implementation:

- **Tool Registration**: ~50ms (startup only)
- **Command Parsing**: <10ms
- **Session Load/Save**: ~30-50ms
- **Principle Lookup**: ~100ms (with caching)
- **Vector Search**: ~200-500ms (Qdrant)
- **Full Analysis**: 5-8 seconds

### Memory Footprint

- **Base MCP Server**: ~50MB
- **TRIZ Knowledge Base**: ~20MB (loaded once)
- **Per Session**: ~1-2MB
- **Vector Embeddings Cache**: ~100MB (optional)

## Implementation Challenges

### 1. MCP Documentation
- Limited official documentation for tool developers
- Need to reverse engineer from examples
- Protocol may change with Claude updates

**Mitigation**: Create abstraction layer, version lock

### 2. Testing MCP Servers
- No official testing framework
- Need to mock Claude CLI environment
- Difficult to test async behavior

**Mitigation**: Create custom test harness, use pytest-asyncio

### 3. Cross-Platform Sessions
- Different metadata between platforms
- Potential format incompatibilities
- Race conditions in concurrent access

**Mitigation**: Use file locks, platform-agnostic schema

## Alternative Approaches Considered

### 1. REST API Bridge
- Create REST API that both Claude and Gemini call
- Pros: Unified interface, easier testing
- Cons: Additional complexity, network latency
- **Decision**: Rejected - adds unnecessary layer

### 2. Direct Claude API Integration
- Use Claude API directly without MCP
- Pros: More control, better documentation
- Cons: Not integrated with Claude CLI
- **Decision**: Rejected - doesn't meet requirements

### 3. Shared Process Model
- Single process serving both Claude and Gemini
- Pros: Resource efficiency, shared state
- Cons: Complex process management
- **Decision**: Rejected - separate processes simpler

## Dependencies Analysis

### New Dependencies Required
```toml
[project.optional-dependencies]
claude = [
    "anthropic-mcp>=0.1.0",  # If available
    "jsonrpc-asyncio>=2.0.0",  # For JSON-RPC
    "aiofiles>=23.0.0",  # Async file operations
]
```

### Compatibility Matrix
- Python 3.11+ ✅ (already required)
- Qdrant ✅ (shared with Gemini)
- Ollama ✅ (shared with Gemini)
- asyncio ✅ (Python stdlib)

## Security Considerations

1. **Command Injection**
   - Sanitize all user inputs
   - Use parameterized commands
   - Avoid shell execution

2. **File Access**
   - Restrict session storage to ~/.triz
   - Validate all file paths
   - Use secure temp files

3. **Resource Limits**
   - Timeout long-running operations
   - Limit session size
   - Rate limit vector searches

## Recommendations

1. **Start with Minimal Implementation**
   - Basic workflow tool only
   - Add solve and direct tools incrementally
   - Focus on core functionality first

2. **Create Abstraction Layer**
   - Platform-agnostic tool interface
   - Easier to add future platforms
   - Simplifies testing

3. **Implement Comprehensive Logging**
   - Debug mode for development
   - Structured logging for production
   - Performance metrics collection

4. **Design for Extensibility**
   - Plugin architecture for new tools
   - Configurable command patterns
   - Modular response formatters

## Open Questions

1. **Official MCP SDK**: Is there an official Python SDK coming?
2. **Streaming Support**: Will Claude MCP support streaming responses?
3. **File Uploads**: Can Claude pass files to MCP tools?
4. **Authentication**: How to handle user-specific sessions?

## Next Steps

1. Create proof-of-concept MCP server
2. Test with simple echo tool
3. Integrate one TRIZ tool
4. Validate session persistence
5. Full implementation if POC successful