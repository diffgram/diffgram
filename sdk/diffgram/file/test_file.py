import random

from diffgram import Project
from diffgram import File


project = Project() 

id = 743

file = project.file.get_by_id(id = id)

assert file.id == id

print(file)
print(file.id)