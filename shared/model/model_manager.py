from shared.database.model.model import Model
from shared.database.model.model_run import ModelRun


class ModelManager:
    """
        This class is for the creation, management and updating of models.
        It contains several helper methods to better manage model runs and
        models in Diffgram.
    """

    def __init__(self, session, instance_list_dicts, project, member):
        self.session = session
        self.instance_list = instance_list_dicts
        self.project = project
        self.member = member

    def check_instances_and_create_new_models(self, use_reference_ids = True):
        """
            This function will go through the instance list, and based on the model run
            reference or the DB ID, create the non existent models and model runs.
        :return: tuple (list of created models, list of created runs)
        """
        create_models = []
        created_runs = []
        for instance in self.instance_list:
            if instance.get('model_ref') is None and instance.get('model_id') is None:
                continue

            model_ref = instance.get('model_ref')
            model_id = instance.get('model_id')
            if use_reference_ids:
                model = Model.get_by_reference_id(self.session, reference_id = model_ref, project_id = self.project.id)
            else:
                model = Model.get_by_id(session = self.session, id = model_id)

            if model is None:
                # Create the new Model if it does not exists.
                model = Model.new(
                    session = self.session,
                    reference_id = model_ref,
                    project_id = self.project.id,
                    member_created_id = self.member.id if self.member else None
                )
                create_models.append(model)
            instance['model_id'] = model.id
            model_run_ref = instance.get('model_run_ref')
            if model_run_ref:
                if use_reference_ids:
                    model_run = ModelRun.get_by_reference_id(self.session,
                                                             reference_id = model_run_ref,
                                                             model_id = model.id)
                else:
                    model_run = ModelRun.get_by_id(self.session, id = instance.get('model_run_id'))
                if model_run is None:
                    # Create the new Model Run
                    model_run = ModelRun.new(
                        session = self.session,
                        reference_id = model_run_ref,
                        project_id = self.project.id,
                        model_id = model.id,
                        member_created_id = self.member.id if self.member else None
                    )
                    created_runs.append(model_run)
                instance['model_run_id'] = model_run.id
        print('RESULT', created_runs, create_models)
        return create_models, created_runs
