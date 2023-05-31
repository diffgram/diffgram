from diffgram.core.core import Project
import random


def generate_random_bounding_box():
    while True:
        x_min = random.randint(0, 2000)
        x_max = random.randint(0, 2000)
        y_min = random.randint(0, 2000)
        y_max = random.randint(0, 2000)

        if x_min < x_max and y_min < y_max and (x_max - x_min) < 50 and (y_max - y_min) < 50:
            return {'x_min': x_min, 'x_max': x_max, 'y_min': y_min, 'y_max': y_max, "name": 'A', 'type': 'box'}


bounding_box = generate_random_bounding_box()

project = Project(
    project_string_id = "test-compounds",
    client_id = "LIVE__hvxq812l74cahekrl7qj",
    client_secret = "w53x665rq517ik1colnhn2t2hn3b42bfdnkzzs2he0yokfqf779gmjrn7pt0",
    debug = True
)
instance_list = []
for i in range(0, 2000):
    bounding_box = generate_random_bounding_box()
    instance_list.append(bounding_box)


project.file.from_url(url = 'https://picsum.photos/2000/2000',
                      instance_list = instance_list,
                      directory_id = 5,
                      file_name='test2.jpeg')
print(bounding_box)
