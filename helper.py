import os, random, shutil, base64

def clear_directory(directory_path):
    """Removes all files and subdirectories inside a given directory without deleting the directory itself."""
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' does not exist.")
        return
    
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Remove files and symbolic links
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directories
        except Exception as e:
            print(f"Failed to delete {item_path}: {e}")


def sample_items(lst, sample_size=150):
    """Randomly sample sample_size items from list without replacement."""
    if len(lst) < sample_size:
        raise ValueError(f"List must have at least {sample_size} items, but has {len(lst)}.")
    return random.sample(lst, sample_size)


def encode_image(image_path):
    """Encodes image at image_path using base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")