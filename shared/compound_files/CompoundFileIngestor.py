from shared.database.source_control.file import File
from shared.database.input import Input
from shared.compound_files.CompoundFile import CompoundFile
from sqlalchemy.orm.session import Session


class CompoundFileUploader:
    session: Session
    log: dict

    def __init__(self, session: Session, log: dict):
        self.session = session
        self.log = log

    def create_from_input(self, input: Input) -> CompoundFile:
        """
            Uploads and create compound file from the provided input
            structure.
        :param compound_file_dict:
        :return:
        """
        if input.type != 'compound':
            msg = f'input.type must be: "compound" to create a compound file'
            self.log['error'] = msg
            return None, self.log
