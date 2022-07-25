import create_task_action_config from "./action_configurations/create_task/create_task_action_config";
import img_properties_outliers_config from "./action_configurations/deepchecks/img_properties_outliers/img_properties_outliers_config";
import export_action_config from "./action_configurations/export/export_action_config";
import AzureTextAnalyticsSentimentAction from "./action_configurations/azure/AzureTextAnalyticsSentimentAction";
import hf_zero_shot from "./action_configurations/hugging_face/HuggingFaceZeroShot.vue"
import VertexTrainDatasetAction from "./action_configurations/VertexTrainDatasetAction/VertexTrainDatasetAction.vue"
//IMPORTREPLACE

export default {
    'AzureTextAnalyticsSentimentAction': AzureTextAnalyticsSentimentAction,
    'export': export_action_config,
    'TaskTemplateActionRunner': create_task_action_config,
    'DeepcheckImagePropertyOutliers': img_properties_outliers_config,
    'hf_zero_shot': hf_zero_shot,
    'VertexTrainDatasetAction': VertexTrainDatasetAction,
    //DECLAREREPLACE
  }