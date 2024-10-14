import json

# Open the JSON file containing annotations
f = open('Downloads/annotations/instances_train2017.json')

# Load the JSON data from the file
data = json.load(f)

# Initialize an empty list to store the processed annotations
result = []


def find(lst, key, value):
    # Iterate through the list of dictionaries
    for i, dic in enumerate(lst):
        # If the specified key's value matches, return the dictionary
        if dic[key] == value:
            return dic
    # If no match is found, return -1
    return -1

# Initialize a counter for the number of annotations processed
i = 0

# Iterate through the list of annotations
for ann in data['annotations']:

    # Extract the image_id and category_id from the current annotation
    im_id = ann['image_id']
    cat_id = ann['category_id']

    # Find the corresponding image and category dictionaries
    img = find(data['images'], 'id', im_id)
    cat = find(data['categories'], 'id', cat_id)

    # Print the current progress
    print(i, len(data['annotations']))

    # Create a new dictionary with the required fields
    current = {
        'x_min': ann['bbox'][0],
        'y_min': ann['bbox'][1],
        'x_max': ann['bbox'][2] + ann['bbox'][0],
        'y_max': ann['bbox'][3] + ann['bbox'][1],
        'image_name': img['file_name'],
        'class': cat['name'],
        'type': 'box',
    }

    # Add the new dictionary to the result list
    result.append(current)

    # Increment the counter
    i += 1

# Open the output JSON file
with open('Downloads/coco2017.json', 'w') as fp:
    # Dump the result list into the output JSON file
    json.dump(result, fp)
