class SensorFusionFileProcessor:
    """
        This class handles the creation of all the files and relationships
        to support sensor fusion annotation.
        This includes, generating point clouds, binding cameras and any
        other data related to the scene to annotate.
    """

    def __init__(self, session, input):
        self.session = session
        self.input = input
