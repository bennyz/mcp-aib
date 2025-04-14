# MCP for AIB

[MCP](https://github.com/modelcontextprotocol) Server for [Automotive Image Builder](https://gitlab.com/CentOS/automotive/src/automotive-image-builder). It doesn't do much besides read and validate the schema to ensure the output is compliant, and can read the source code.

## Installation

```shell
$ uv venv
$ source venv/bin/activate
$ uv run mcp dev # debug with inspector
$ uv run mcp install # install in claude desktop
```

Install in VSCode:
```
$ code --add-mcp '{"name":"aib","command":"uv","args":["run", "--with", "mcp[cli]", "--with", "pyyaml", "--with", "jsonschema", "mcp", "run", "/path/to/mcp-aib/server.py"]}'
```

## Tools available

- validate_yaml
- get_schema
- get_directory_tree
- read_file
