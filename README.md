# MCP for AIB

[MCP](https://github.com/modelcontextprotocol) Server for [Automotive Image Builder](https://gitlab.com/CentOS/automotive/src/automotive-image-builder). It doesn't do much besides read and validate the schema to ensure the output is compliant, and can read the source code.

## Clone

```shell
git clone --recursive https://github.com/bennyz/mcp-aib.git
```

## Installation

```shell
$ uv run mcp dev server.py # debug with inspector
$ uv run mcp install server.py --with-editable . # install in claude desktop
```

Install in VSCode:
```
$ code --add-mcp '{"name":"aib","command":"uv","args":["run", "--with-editable", "/path/to/mcp-aib", "mcp", "run", "/path/to/mcp-aib/server.py"]}'
```

Replace `/path/to/mcp-aib` with the actual path to your mcp-aib directory.

## Tools available

- validate_yaml
- get_schema
- get_directory_tree
- read_file
- get_available_targets
- get_available_distros
- generate_build_command