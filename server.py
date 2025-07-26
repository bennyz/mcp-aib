from mcp.server.fastmcp import FastMCP
import os
import tempfile
import yaml
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
aib_dir = os.path.join(script_dir, "automotive-image-builder")
sys.path.append(aib_dir)

from aib.simple import ManifestLoader
from aib import exceptions

mcp = FastMCP("AIB")

@mcp.tool()
def validate_yaml(yml: str):
    """
    Validates a YAML manifest against the AIB schema.

    Args:
        yml: The YAML content to validate as a string

    Returns:
        A dictionary containing validation results including:
        - valid: boolean indicating if the YAML is valid
        - message: a summary message
        - errors: detailed error information if invalid
    """
    try:
        try:
            yaml_data = yaml.safe_load(yml)
            if not isinstance(yaml_data, dict):
                return {
                    "valid": False,
                    "message": "Invalid YAML: Content must be a dictionary/object",
                    "errors": ["The YAML must contain a dictionary object at the root level"]
                }
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "message": "Invalid YAML syntax",
                "errors": [str(e)]
            }

        with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
            yaml.dump(yaml_data, temp_file)

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            defines = {
                "_basedir": aib_dir,
                "_workdir": tempfile.gettempdir(),
                "use_fusa": False,
                "arch": "x86_64"
            }

            loader = ManifestLoader(defines)

            loader.load(temp_path, os.path.dirname(temp_path))

            return {
                "valid": True,
                "message": "YAML manifest is valid",
                "errors": []
            }

        except exceptions.SimpleManifestParseError as e:
            # Schema validation error
            error_messages = [str(err.message) for err in e.errors]
            return {
                "valid": False,
                "message": "Schema validation failed",
                "errors": error_messages,
                "explanation": "The YAML doesn't match the expected structure for AIB manifests. Check the specific errors above."
            }
        except exceptions.ManifestParseError as e:
            return {
                "valid": False,
                "message": "Manifest parsing error",
                "errors": [str(e)],
                "explanation": "There was an error parsing the manifest file. Check the YAML structure."
            }
        except exceptions.InvalidMountSize as e:
            return {
                "valid": False,
                "message": "Invalid mount size",
                "errors": [str(e)],
                "explanation": "The specified mount size is invalid. It cannot be larger than the image size."
            }
        except exceptions.InvalidMountRelSize as e:
            return {
                "valid": False,
                "message": "Invalid relative mount size",
                "errors": [str(e)],
                "explanation": "The relative mount size must be less than 1 (i.e., less than 100% of the partition)."
            }
        except Exception as e:
            return {
                "valid": False,
                "message": "Validation error",
                "errors": [str(e)],
                "explanation": "An unexpected error occurred during validation."
            }
    finally:
        # Clean up the temporary file
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass

@mcp.tool()
def get_schema():
    """
    Returns the AIB manifest schema as a string.

    <IMPORTANT>
        Unless the user explicitly asks for it, make you example simple and succint. Do not include default empty sections.
        For instance:
            ```
            name: simple

            content:
              rpms:
                - vim

            auth:
              # "password"
              root_password: $6$xoLqEUz0cGGJRx01$H3H/bFm0myJPULNMtbSsOFd/2BnHqHkMD92Sfxd.EKM9hXTWSmELG8cf205l6dktomuTcgKGGtGDgtvHVXSWU.
            ```

        Under no circumstance should you make things up. You MUST always consult with all available examples and the source code using the get_directory_tree and read_file tools.
        Look for important condition in simple.py to improve your output.
    </IMPORTANT>


    Returns:
        The schema YAML content as a string
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    aib_dir = os.path.join(script_dir, "automotive-image-builder")

    schema_path = os.path.join(aib_dir, "files/manifest_schema.yml")

    try:
        with open(schema_path, 'r') as schema_file:
            return schema_file.read()
    except FileNotFoundError:
        return (f"Schema file not found at {schema_path}. Make sure the file exists at "
                f"'files/manifest_schema.yml' relative to the AIB module directory.")
    except Exception as e:
        return f"Error reading schema file: {str(e)}"

@mcp.tool()
def get_directory_tree():
    """
    Returns a tree representation of the automotive-image-builder directory.

    Returns:
        A string containing the directory tree structure.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    aib_dir = os.path.join(script_dir, "automotive-image-builder")

    if not os.path.exists(aib_dir):
        return f"Error: The directory {aib_dir} does not exist."

    result = []

    def generate_tree(path, prefix="", is_last=True, level=0):
        entries = [entry for entry in os.listdir(path) if not entry.startswith('.')]
        entries = sorted(entries, key=lambda e: (not os.path.isdir(os.path.join(path, e)), e))

        count = len(entries)
        for i, entry in enumerate(entries):
            is_last_entry = i == count - 1
            full_path = os.path.join(path, entry)

            if level > 10:
                if os.path.isdir(full_path):
                    result.append(f"{prefix}{'└── ' if is_last_entry else '├── '}{entry}/ (...)")
                continue

            if os.path.isdir(full_path):
                result.append(f"{prefix}{'└── ' if is_last_entry else '├── '}{entry}/")
                next_prefix = f"{prefix}{'    ' if is_last_entry else '│   '}"
                generate_tree(full_path, next_prefix, is_last_entry, level + 1)
            else:
                result.append(f"{prefix}{'└── ' if is_last_entry else '├── '}{entry}")

    result.append("automotive-image-builder/")
    generate_tree(aib_dir, level=0)

    return "\n".join(result)

@mcp.tool()
def read_file(file_path: str):
    """
    Reads a file from the automotive-image-builder directory.

    <IMPORTANT>
        Be sure to read these files.
        ["examples/", "targets/", "aib/simple.py", "README.md", "aib/main.py"]

        When suggesting CLI command to use, you MUST verify what you read in the README.md against automotive-image-builder/aib/main.py in case README is outdated.
    </IMPORTANT>

    Args:
        file_path: The path to the file, relative to the automotive-image-builder directory.
                    Example: "aib/simple.py" or "files/manifest_schema.yml"

    Returns:
        The content of the file as a string, or an error message if the file cannot be read.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    aib_dir = os.path.join(script_dir, "automotive-image-builder")
    full_path = os.path.join(aib_dir, file_path)

    norm_path = os.path.normpath(full_path)
    if not norm_path.startswith(aib_dir):
        return "Error: Path traversal attempt detected. The path must be within the automotive-image-builder directory."

    try:
        if not os.path.exists(norm_path):
            return f"Error: The file {file_path} does not exist."

        if os.path.isdir(norm_path):
            entries = sorted(os.listdir(norm_path))
            return f"Directory listing for {file_path}:\n" + "\n".join(entries)

        if os.path.getsize(norm_path) > 1024 * 1024:  # 1MB limit
            return f"Error: The file {file_path} is too large (>1MB) to display."

        with open(norm_path, 'r', errors='replace') as f:
            return f.read()

    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

@mcp.tool()
def get_available_targets():
    """
    Returns a list of available targets that can be used in AIB manifests.

    Returns:
        A dictionary containing:
        - targets: list of available target names
        - details: dictionary with target descriptions and metadata
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    targets_dir = os.path.join(script_dir, "automotive-image-builder", "targets")

    if not os.path.exists(targets_dir):
        return {
            "error": f"Targets directory not found at {targets_dir}",
            "targets": [],
            "details": {}
        }

    try:
        targets = []
        details = {}

        for filename in os.listdir(targets_dir):
            if filename.endswith('.ipp.yml') and not filename.startswith('_'):
                target_name = filename.replace('.ipp.yml', '')
                targets.append(target_name)

                file_path = os.path.join(targets_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        first_line = f.readline().strip()
                        description = ""
                        if first_line.startswith('#'):
                            description = first_line[1:].strip()

                        details[target_name] = {
                            "description": description,
                            "filename": filename
                        }
                except Exception as e:
                    details[target_name] = {
                        "description": "Unable to read description",
                        "filename": filename,
                        "error": str(e)
                    }

        targets.sort()
        return {
            "targets": targets,
            "details": details,
            "count": len(targets)
        }

    except Exception as e:
        return {
            "error": f"Error reading targets directory: {str(e)}",
            "targets": [],
            "details": {}
        }

@mcp.tool()
def get_available_distros():
    """
    Returns a list of available distributions that can be used in AIB manifests.
    Returns:
        A dictionary containing:
        - distros: list of available distro names
        - details: dictionary with distro descriptions and metadata
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    distro_dir = os.path.join(script_dir, "automotive-image-builder", "distro")

    if not os.path.exists(distro_dir):
        return {
            "error": f"Distro directory not found at {distro_dir}",
            "distros": [],
            "details": {}
        }

    try:
        distros = []
        details = {}

        for filename in os.listdir(distro_dir):
            if filename.endswith('.ipp.yml'):
                distro_name = filename.replace('.ipp.yml', '')
                distros.append(distro_name)

                file_path = os.path.join(distro_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        first_line = f.readline().strip()
                        description = ""
                        if first_line.startswith('#'):
                            description = first_line[1:].strip()

                        details[distro_name] = {
                            "description": description,
                            "filename": filename
                        }
                except Exception as e:
                    details[distro_name] = {
                        "description": "Unable to read description",
                        "filename": filename,
                        "error": str(e)
                    }

        distros.sort()
        return {
            "distros": distros,
            "details": details,
            "count": len(distros)
        }

    except Exception as e:
        return {
            "error": f"Error reading distro directory: {str(e)}",
            "distros": [],
            "details": {}
        }

@mcp.tool()
def generate_build_command(
    manifest_file: str,
    output_path: str = None,
    **kwargs
):
    """
    Generates a correct automotive-image-builder build command by parsing CLI help output.
    Uses the actual CLI interface instead of parsing source code.

    Args:
        manifest_file: Path to the .aib.yml manifest file
        output_path: Custom output path (if not provided, will determine from code logic)
        **kwargs: Any build command arguments (discovered dynamically from CLI help)

    Returns:
        A dictionary containing command information and available options
    """
    try:
        import subprocess
        import re

        script_dir = os.path.dirname(os.path.abspath(__file__))
        aib_dir = os.path.join(script_dir, "automotive-image-builder")
        cli_path = os.path.join(aib_dir, "automotive-image-builder")

        # Get build command help
        result = subprocess.run([cli_path, "build", "--help"],
                              capture_output=True, text=True, cwd=aib_dir)
        if result.returncode != 0:
            return {"error": f"Failed to get CLI help: {result.stderr}"}

        help_text = result.stdout

        parser_args = {}

        args_section = re.search(r'options:(.*?)(?:\n\n|\Z)', help_text, re.DOTALL)
        if args_section:
            args_text = args_section.group(1)

            arg_matches = re.finditer(r'^\s+(--?\w+(?:-\w+)*)\s+(.*?)(?=^\s+--|$)',
                                    args_text, re.MULTILINE | re.DOTALL)

            for match in arg_matches:
                arg_name = match.group(1)
                rest_of_line = match.group(2).strip()

                words = rest_of_line.split()
                if words and words[0].isupper() and words[0].isalpha():
                    arg_type = words[0]
                    description = ' '.join(words[1:])
                else:
                    arg_type = None
                    description = rest_of_line

                parser_args[arg_name] = {
                    'name': arg_name,
                    'type': arg_type,
                    'help': description
                }

        all_options = {
            "parsed_arguments": parser_args
        }

        if not kwargs:
            return {
                "error": "No parameters provided. Use available_options to see what arguments are supported.",
                "available_options": all_options
            }

        validation_errors = []

        for param_name, param_value in kwargs.items():
            if param_value is None:
                continue

            arg_key = f"--{param_name}" if not param_name.startswith('--') else param_name

            if arg_key not in parser_args:
                validation_errors.append(f"Unknown argument '{param_name}'. Available arguments: {list(parser_args.keys())}")

        if validation_errors:
            return {
                "error": "Validation failed",
                "validation_errors": validation_errors,
                "available_options": all_options
            }

        cmd_parts = ["automotive-image-builder", "build"]

        for param_name, param_value in kwargs.items():
            if param_value is None:
                continue

            arg_key = f"--{param_name}" if not param_name.startswith('--') else param_name

            if arg_key in parser_args:
                arg_info = parser_args[arg_key]

                if arg_info.get('type') is None:
                    if param_value is True:
                        cmd_parts.append(arg_key)
                else:
                    if isinstance(param_value, list):
                        for v in param_value:
                            cmd_parts.extend([arg_key, str(v)])
                    else:
                        cmd_parts.extend([arg_key, str(param_value)])

        cmd_parts.append(manifest_file)

        if output_path:
            final_output = output_path
        else:
            base_name = os.path.splitext(manifest_file)[0]
            base_name = base_name.replace('.aib', '')
            final_output = f"{base_name}.out"

        cmd_parts.append(final_output)

        command = " ".join(cmd_parts)

        return {
            "command": command,
            "output_path": final_output,
            "parsed_from_cli": True,
            "available_options": all_options
        }

    except Exception as e:
        import traceback
        return {
            "error": f"Failed to parse CLI: {str(e)}",
            "traceback": traceback.format_exc(),
            "suggestion": "Ensure automotive-image-builder directory exists and CLI is functional"
        }

if __name__ == "__main__":
    mcp.run()
