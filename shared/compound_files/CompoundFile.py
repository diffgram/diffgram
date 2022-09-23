from shared.database.source_control.file import File
from typing import List


class CompoundFile:
    parent_file: File
    child_file_list: List[File]
