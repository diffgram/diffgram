
class ModelManager:
    """
        This class is for the creation, management and updating of models.
        It contains several helper methods to better manage model runs and
        models in Diffgram.
    """

    def __init__(self, session, instance_list, project):
        self.session = session
        self.instance_list = instance_list
        self.project = project

    def check_instances_and_create_new_models(self, use_reference_ids = True):
        """
            This function will go through the instance list and based on the model run
            reference or the DB ID, create the non existent models and model runs.
        :return: tuple (list of created models, list of created runs)
        """
        raise NotImplementedError

