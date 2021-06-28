
from shared.database_setup_supporting import *
from shared.helpers.sessionMaker import session_factory

"""
This script looks for all the instances that still don't have their 
parent file id populated and adds it to the parent_file_id column.
"""
session = session_factory()

instances = session.query(Instance).join(File, Instance.id == File.id).filter(
    File.type == 'frame',
    Instance.parent_file_id == None
).all()

print(len(instances), 'instances')

i = 0
for instance in instances:
    file = File.get_by_id(session, instance.file_id)
    instance.parent_file_id = file.video_parent_file_id
    session.add(instance)

session.commit()