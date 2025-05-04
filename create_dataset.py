import json, os, random, shutil, sys
from PIL import Image
from helper import *

def get_dataset_statistics(data_objs):
    """Calculate and display number of one object, two object, and camera, human, unknown perspective instances"""
    one_obj_camera = 0
    one_obj_human = 0
    one_obj_unknown = 0
    two_obj_camera = 0
    two_obj_human = 0
    two_obj_unknown = 0

    for data in data_objs:
        is_one_obj = True if data["object2"] == "" else False


        if "camera" in data["question"] and "perspective" in data["question"]:
            if is_one_obj:
                one_obj_camera += 1
            else: 
                two_obj_camera += 1
        elif "perspective" in data["question"]:
            if is_one_obj:
                one_obj_human += 1
            else: 
                two_obj_human += 1
        else: 
            if is_one_obj:
                one_obj_unknown += 1
            else: 
                two_obj_unknown += 1

    print(f"One object:\n\tCamera: {one_obj_camera}\n\tHuman: {one_obj_human}\n\tUnknown: {one_obj_unknown}")
    print(f"Two object:\n\tCamera: {two_obj_camera}\n\tHuman: {two_obj_human}\n\tUnknown: {two_obj_unknown}")

def rotate_images(input_dir, output_dir, degrees):
    """Rotates all .jpg images in input_dir by the given degrees and saves them in output_dir."""
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".png"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                with Image.open(input_path) as img:
                    rotated_img = img.rotate(degrees, expand=True)  # Rotate and resize canvas if needed
                    rotated_img.save(output_path)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")


with open("data/spatial_mm_one_obj.json", "r", encoding="utf-8") as f:
    one_obj_data = json.load(f)

with open("data/spatial_mm_two_obj.json", "r", encoding="utf-8") as f:
    two_obj_data = json.load(f)


img_dir = "data/imgs"
print(f"Total {len(os.listdir(img_dir))} images in directory.")
print(f"Total {len(one_obj_data)} one_obj instances")
print(f"Total {len(two_obj_data)} two_obj instances")


print("Statistics for original dataset")
get_dataset_statistics(one_obj_data+two_obj_data)


filtered_one_obj = []
for q_dict in one_obj_data: 
    # Filter out unwanted spatial relationships
    rel_split = q_dict["answer"].split(" ")
    if len(rel_split) != 2:
        continue
    elif rel_split[-1] not in ["left", "right", "top", "bottom", "down", "up", "top", "upwards", "above"]:
        continue        

    # Add tag for perpective
    if "camera" in q_dict["question"] and "perspective" in q_dict["question"]:
        q_dict["perspective"] = "camera"
    elif "perspective" in q_dict["question"]:
        q_dict["perspective"] = "human"
    else: 
        q_dict["perspective"] = "unk"

    # Add tag for number of objects
    q_dict["num_obj"] = "one"

    filtered_one_obj.append(q_dict)


filtered_two_obj = []
for q_dict in two_obj_data: 
    rel_split = q_dict["answer"].split(" ")
    if len(rel_split) != 2:
        continue
    elif rel_split[-1] not in ["left", "right", "top", "below", "above", "behind", "front"]:
        continue

    # Add tag for perpective
    if "camera" in q_dict["question"] and "perspective" in q_dict["question"]:
        q_dict["perspective"] = "camera"
    elif "perspective" in q_dict["question"]:
        q_dict["perspective"] = "human"
    else: 
        q_dict["perspective"] = "unk"

    # Add tag for number of objects
    q_dict["num_obj"] = "two"

    filtered_two_obj.append(q_dict)

print("Statistics for filtered dataset")
get_dataset_statistics(filtered_one_obj+filtered_two_obj)

filtered_one_obj = sample_items(filtered_one_obj)
filtered_two_obj = sample_items(filtered_two_obj)
all_data = filtered_one_obj + filtered_two_obj

sampled_data = []
for q_dict in all_data:
    try:
        img_name = q_dict["image_name"]
        old_img_fp = f"data/imgs/{img_name}"
        new_img_fp = f"data/filtered_imgs/{img_name}"
        shutil.copy2(old_img_fp, new_img_fp)
        sampled_data.append(q_dict)
    except FileNotFoundError:
        print(f"{img_name} not found, skipping")
        continue

print("Statistics for sampled dataset")
get_dataset_statistics(sampled_data)


with open(f"data/filtered_dataset.json", "w", encoding="utf-8") as f:
    clear_directory("data/filtered_imgs")
    json.dump(sampled_data, f, indent=4, ensure_ascii=False)


rotate_images("data/filtered_imgs", "data/rotate90_imgs", 90)
rotate_images("data/filtered_imgs", "data/rotate180_imgs", 180)
rotate_images("data/filtered_imgs", "data/rotate270_imgs", 270)