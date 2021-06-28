from lark.visitors import Visitor


class DiffgramQuery:
    """
        The Diffgram Query Object is a tree visitors that
        can be traversed to generate relevant output for different
        usecases. This object is the input for classes that implement
        the DiffgramQueryExecutor.
    """

    def __init__(self, tree, project, member, directory = None):
        self.tree = tree
        self.project = project
        self.member = member
        self.directory = directory
