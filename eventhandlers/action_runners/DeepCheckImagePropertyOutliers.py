from eventhandlers.action_runners.base.ActionRunner import ActionRunner
from deepchecks.vision.checks import ImagePropertyOutliers
from deepchecks.vision import VisionData
from deepchecks.vision.datasets.detection.coco import load_dataset
from skimage import io, transform
from sqlalchemy.orm import Session
from torch.utils.data import DataLoader
from io import BytesIO
from shared.database.source_control.working_dir import WorkingDir
from shared.database.source_control.working_dir import WorkingDirFileLink
from shared.helpers.sessionMaker import session_scope
from shared.database.source_control.file import File
from shared.database.project import Project
from shared.data_tools_core import Data_tools

data_tools = Data_tools().data_tools


class DiffgramVisionDataset(VisionData):
    session: Session
    diffgram_dir_id: int
    diffgram_dir: WorkingDir

    def __init__(self, session, diffgram_dir_id):
        self.session = session
        self.diffgram_dir_id = diffgram_dir_id
        query, count = WorkingDirFileLink.file_list(
            session = self.session,
            working_dir_id = self.diffgram_dir_id,
            type = ['image'],
            return_mode = "query",
            limit = None,
            order_by_class_and_attribute = File.id,
            count_before_limit = True
        )
        self.file_list = query.all()
        self.count = count

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        file = self.file_list[idx]
        file.image.regenerate_url(session = self.session)
        bytes_img = data_tools.download_bytes()
        res = BytesIO(bytes_img)
        image = io.imread(res)
        sample = {'image': image}

        if self.transform:
            sample = self.transform(sample)

        return sample


class DeepcheckImagePropertyOutliers(ActionRunner):
    public_name = 'Deep Check - Image Properties Outliers'
    description = 'Image Properties Outliers'
    icon = 'https://finder.startupnationcentral.org/image_cloud/deepchecks_22b0d93d-3797-11ea-aa4a-bd6ae2b3f19f?w=240&h=240'
    kind = 'deep_checks__image_properties_outliers'  # The kind has to be unique to all actions
    category = 'Training Data Checks'  # Optional
    trigger_data = {'trigger_event_name': 'input_file_uploaded'}  # What events can this action listen to?
    condition_data = {'event_name': None}  # What pre-conditions can this action have?
    completion_condition_data = {
        'event_name': 'action_completed'}  # What options are available to declare the actions as completed?

    def execute_pre_conditions(self, session, action) -> bool:
        # Return true if no pre-conditions are needed.
        return True

    def execute_action(self, session):
        # Your core Action logic will go here.
        vision_ds = DiffgramVisionDataset(session = session, diffgram_dir_id = 1)
        dataset_loader = DataLoader(vision_ds, batch_size = 1000, num_workers = 2)
        # TODO: Load and transform diffgram dataset
        train_data = load_dataset(train = True, object_type = 'VisionData')
        check = ImagePropertyOutliers()
        result = check.run(train_data)
