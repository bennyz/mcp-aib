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
                "_basedir": aib_dir,  # Path to the directory containing aib module
                "_workdir": tempfile.gettempdir(),  # Use temp dir as working dir
                "use_fusa": False,  # Not using FUSA mode
                "arch": "x86_64"  # Default architecture
            }

            loader = ManifestLoader(defines)

            loader.load(temp_path, os.path.dirname(temp_path))

            return {
                "valid": True,
                "message": "YAML manifest is valid",
                "errors": []
            }

        except exceptions.SimpleManifestParseError as e:
            # Schema validation errors
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
