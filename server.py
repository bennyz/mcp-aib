from mcp.server.fastmcp import FastMCP
import os
import tempfile
import yaml
from aib import ManifestLoader, exceptions

mcp = FastMCP("Demo")

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
        # Parse the YAML first to catch basic syntax errors
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

        # Create a temporary file to use with the loader
        with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w', delete=False) as temp_file:
            temp_path = temp_file.name
            yaml.dump(yaml_data, temp_file)

        try:
            # Set up required defines for the manifest loader
            script_dir = os.path.dirname(os.path.abspath(__file__))
            defines = {
                "_basedir": script_dir,  # Path to the directory containing aib.py
                "_workdir": tempfile.gettempdir(),  # Use temp dir as working dir
                "use_fusa": False,  # Not using FUSA mode
                "arch": "x86_64"  # Default architecture
            }

            # Create a manifest loader with our defines
            loader = ManifestLoader(defines)

            # Validate the manifest
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

    Returns:
        The schema YAML content as a string
    """
    # Get the base directory (same as used in ManifestLoader)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the schema file
    schema_path = os.path.join(script_dir, "files/manifest_schema.yml")

    # Read and return the schema file content
    try:
        with open(schema_path, 'r') as schema_file:
            return schema_file.read()
    except FileNotFoundError:
        return (f"Schema file not found at {schema_path}. Make sure the file exists at "
                f"'files/manifest_schema.yml' relative to the directory containing aib.py.")
    except Exception as e:
        return f"Error reading schema file: {str(e)}"
