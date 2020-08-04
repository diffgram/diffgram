import random

from diffgram import Project
from diffgram import File


project = Project() 

id = 2

task = project.task.get_by_id(id = id)

print(task)

assert task.id == id

print(task.file)
print(task.file.id)
