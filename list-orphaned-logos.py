import yaml
import os
import sys
from collections.abc import Mapping, Sequence # Use collections.abc for modern Python

# --- Configuration ---
YAML_FILE_PATH = './landscape.yml'
LOGO_DIR_PATH = './hosted_logos'
LOGO_EXTENSION = '.svg' # Focus on SVG files
# --- End Configuration ---

def find_logos_recursive(data, found_logos):
    """Recursively searches for 'logo' keys in nested data structures."""
    if isinstance(data, Mapping): # Check if it's dictionary-like
        if 'logo' in data and isinstance(data['logo'], str) and data['logo']:
            # Add the logo filename if it's a non-empty string
            found_logos.add(data['logo'])
        # Recursively search in dictionary values
        for key, value in data.items():
            find_logos_recursive(value, found_logos)
    elif isinstance(data, Sequence) and not isinstance(data, str): # Check if it's list/tuple-like (but not a string)
        # Recursively search in list/tuple items
        for item in data:
            find_logos_recursive(item, found_logos)
    # Ignore other data types (like strings, numbers, booleans)

def find_unused_logos(yaml_path, logo_dir, extension):
    """
    Finds logo files in a directory that are not referenced
    in a given YAML file.
    """
    referenced_logos = set()

    # 1. Read and parse the YAML file to find referenced logos
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
                if data: # Ensure the file wasn't empty
                    find_logos_recursive(data, referenced_logos)
                print(f"Found {len(referenced_logos)} unique logo references in '{yaml_path}'.")
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file '{yaml_path}': {e}", file=sys.stderr)
                return None # Indicate failure
            except Exception as e:
                print(f"An unexpected error occurred while processing YAML: {e}", file=sys.stderr)
                return None # Indicate failure

    except FileNotFoundError:
        print(f"Error: YAML file not found at '{yaml_path}'", file=sys.stderr)
        return None # Indicate failure
    except IOError as e:
        print(f"Error reading YAML file '{yaml_path}': {e}", file=sys.stderr)
        return None # Indicate failure

    # 2. List logo files in the specified directory
    existing_logo_files = set()
    try:
        if not os.path.isdir(logo_dir):
             print(f"Error: Logo directory not found or is not a directory at '{logo_dir}'", file=sys.stderr)
             return None # Indicate failure

        print(f"Scanning directory '{logo_dir}' for '{extension}' files...")
        for filename in os.listdir(logo_dir):
            # Check if it's a file and ends with the specified extension (case-insensitive)
            if filename.lower().endswith(extension) and \
               os.path.isfile(os.path.join(logo_dir, filename)):
                existing_logo_files.add(filename)

        print(f"Found {len(existing_logo_files)} '{extension}' files in '{logo_dir}'.")

    except OSError as e:
        print(f"Error accessing logo directory '{logo_dir}': {e}", file=sys.stderr)
        return None # Indicate failure
    except Exception as e:
        print(f"An unexpected error occurred while scanning directory: {e}", file=sys.stderr)
        return None # Indicate failure


    # 3. Find the difference: files in directory but not in YAML references
    unused_logos = existing_logo_files - referenced_logos

    return list(unused_logos) # Return the list of unused logo filenames

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting unused logo check...")
    unused = find_unused_logos(YAML_FILE_PATH, LOGO_DIR_PATH, LOGO_EXTENSION)

    if unused is not None: # Check if the function executed successfully
        if not unused:
            print("\nResult: All '{LOGO_EXTENSION}' files in '{LOGO_DIR_PATH}' seem to be referenced in '{YAML_FILE_PATH}'.")
        else:
            print(f"\nResult: Found {len(unused)} unused '{LOGO_EXTENSION}' files:")
            # Sort for consistent output
            unused.sort()
            for logo_file in unused:
                print(f"rm \"{LOGO_DIR_PATH}/{logo_file}\"")
            print(f"\nConsider removing these files from '{LOGO_DIR_PATH}' if they are no longer needed.")
    else:
        print("\nScript finished with errors.", file=sys.stderr)
        sys.exit(1) # Exit with error code

    print("\nScript finished successfully.")