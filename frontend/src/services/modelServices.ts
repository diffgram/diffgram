import axios from "./customInstance";

export const get_model_run_list = async (
  project_string_id: string, 
  model_run_id_list: any[]
) => {
  try {
    const response = await axios.post(
      `/api/v1/project/${project_string_id}/model-runs/list`,
      { id_list: model_run_id_list.map((x) => parseInt(x, 10)) }
    );

    return [response.data, null]
  } catch (e) {
    return [null, e]
  }
}