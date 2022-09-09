from shared.database_setup_supporting import *
from shared.helpers.sessionMaker import session_factory, session_scope
from shared.database.source_control.file_stats import FileStats
with session_scope() as session:
    files = session.query(File.id).filter(File.id >= 152849).all()
    print('Files', files)


    def update_file_stats(file_elm, session):
        file_id = file_elm[0]

        file = File.get_by_id(session, file_id = file_id)
        print(f'Creating Stats for file ID: {file_id}')
        if file.project:
            FileStats.update_file_stats_data(
                session = session,
                instance_list = file.cache_dict.get('instance_list', []) if file.cache_dict else [],
                file_id = file.id,
                project = file.project
            )
            session.commit()

    for file_elm in files:
        update_file_stats(file_elm, session)