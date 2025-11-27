import os
import json

# This is a mock implementation of the MCP services for local development.
# It uses the local filesystem to simulate a "SmartBucket".

STORAGE_DIR = "mcp_storage"
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def _get_file_path(bucket_name, key):
    """Converts a bucket/key into a local file path."""
    bucket_path = os.path.join(STORAGE_DIR, bucket_name)
    # Sanitize key to be a valid relative path
    key_path = key.replace("..", "").replace("/", os.sep)
    if os.path.isabs(key_path):
        key_path = key_path[1:]
    return os.path.join(bucket_path, key_path)

def put_object(bucket_name: str, key: str, content: str):
    """Mocks the put_object functionality by saving content to a local file."""
    file_path = _get_file_path(bucket_name, key)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)
    print(f"[mock_mcp] Saved object to {file_path}")

def get_object(bucket_name: str, key: str) -> str:
    """Mocks the get_object functionality by reading content from a local file."""
    file_path = _get_file_path(bucket_name, key)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"[mock_mcp] No object found for key: '{key}' in bucket '{bucket_name}'")
        
    with open(file_path, "r") as f:
        content = f.read()
    print(f"[mock_mcp] Retrieved object from {file_path}")
    return content

def list_objects(bucket_name: str, prefix: str = "") -> list[dict]:
    """Mocks the list_objects functionality by listing files in a local directory."""
    bucket_path = os.path.join(STORAGE_DIR, bucket_name)
    
    if not os.path.exists(bucket_path):
        return []

    object_keys = []
    prefix_dir = os.path.join(bucket_path, prefix.replace("/", os.sep))
    
    if not os.path.exists(prefix_dir):
        return []

    for dirpath, _, filenames in os.walk(prefix_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            key = os.path.relpath(full_path, bucket_path).replace(os.sep, "/")
            object_keys.append({'key': key})
            
    print(f"[mock_mcp] Listed {len(object_keys)} objects in bucket '{bucket_name}' with prefix '{prefix}'")
    return object_keys
