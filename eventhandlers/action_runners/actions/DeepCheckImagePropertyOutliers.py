#import cv2
from action_runners.base.ActionRunner import ActionRunner
from deepchecks.vision.checks import ImagePropertyOutliers
from deepchecks.vision import VisionData
from deepchecks.core.serialization.check_result.html import CheckResultSerializer as CheckResultHtmlSerializer
from PIL import Image
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
from torch.utils.data import Dataset, DataLoader
import numpy as np
from action_runners.base.ActionTrigger import ActionTrigger
from action_runners.base.ActionCondition import ActionCondition
from action_runners.base.ActionCompleteCondition import ActionCompleteCondition
import skimage

data_tools = Data_tools().data_tools


class DiffgramDataset(Dataset):
    def __init__(self, session: Session, diffgram_dir_id: int):
        #self.session = session
        self.diffgram_dir_id = diffgram_dir_id
        query, count = WorkingDirFileLink.file_list(
            session = session,
            working_dir_id = self.diffgram_dir_id,
            type = ['image'],
            return_mode = "query",
            limit = None,
            order_by_class_and_attribute = File.id,
            count_before_limit = True
        )
        self.file_list = []
        for file in query.all():
            #file.image.regenerate_url(session = self.session)
            self.file_list.append(file.serialize_with_type(session = session))
        self.count = count

    def __len__(self) -> int:
        return len(self.file_list)

    def __getitem__(self, idx: int) -> np.ndarray:
        file = self.file_list[idx]
        bytes_img = data_tools.download_bytes(file.get('image').get('url_signed_blob_path'))
        res = BytesIO(bytes_img)
        image = io.imread(res)
        PIL_image = Image.fromarray(np.uint8(image)).convert('RGB')
        final_image = np.asarray(PIL_image)
        #img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return final_image


class DiffgramVisionDataset(VisionData):
    def batch_to_images(self, batch):
        """
        """
        return batch


class DeepcheckImagePropertyOutliers(ActionRunner):
    public_name = 'Deep Check - Image Properties Outliers'
    description = 'Image Properties Outliers'
    icon = 'https://media-exp1.licdn.com/dms/image/C560BAQHFz-PWwUqWvg/company-logo_200_200/0/1579104155214?e=2147483647&v=beta&t=own-JfrDFxlz6goCBucZZ65OcB3l3nQPAzX4q3oN1yE'
    kind = 'DeepcheckImagePropertyOutliers'
    trigger_data = ActionTrigger(default_event = 'input_file_uploaded',
                                 event_list = ['input_file_uploaded', 'task_completed'])
    precondition = ActionCondition(default_event = None, event_list = [])
    completion_condition_data = ActionCompleteCondition(default_event = None, event_list = [])

    def execute_pre_conditions(self, session) -> bool:
        # Return true if no pre-conditions are needed.
        return True

    def execute_action(self, session):
        # Your core Action logic will go here.
        dir_id = self.event_data.get('directory_id')
        pytorch_dataset = DiffgramDataset(session = session, diffgram_dir_id = dir_id)
        dataloader = DataLoader(pytorch_dataset, batch_size = 5, shuffle = True, num_workers = 0, collate_fn = lambda data: data)
        vision_ds = DiffgramVisionDataset(data_loader = dataloader)
        check = ImagePropertyOutliers()
        result = check.run(vision_ds)
        html = CheckResultHtmlSerializer(result).serialize(
            output_id = None,
            full_html = True,
            include_requirejs = True,
            include_plotlyjs = True
        )

        url = self.save_html_output(session = session, html_data = html)
        return True