import json

f = open('Downloads/annotations/instances_train2017.json')
x = json.load(f)

result = []


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return dic
    return -1

i = 0
for ann in x['annotations']:

    im_id = ann['image_id']
    cat_id = ann['category_id']
    img = find(x['images'], 'id', im_id)
    cat = find(x['categories'], 'id', cat_id)
    print(i, len(x['annotations']))
    current = {
        'x_min': ann['bbox'][0],
        'y_min': ann['bbox'][1],
        'x_max': ann['bbox'][2] + ann['bbox'][0],
        'y_max': ann['bbox'][3] + ann['bbox'][1],
        'image_name': img['file_name'],
        'class': cat['name'],
        'type': 'box',
    }
    result.append(current)
    i += 1
with open('Downloads/coco2017.json', 'w') as fp:
    json.dump(result, fp)
