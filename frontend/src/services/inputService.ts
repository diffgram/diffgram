
import axios from './customInstance';

export type InputListRequestData = {
  limit: number,
  show_archived: boolean,
  show_deferred: boolean,
  status_filter: string,
  date_from: Date,
  date_to: Date,
  file_id: number,
  parent_file_id: number,
  batch_id: number,
  media_type: string,
  task_id: number,
  has_attached_instances: boolean


}
export const fetch_input_list = async (project_string_id: string, filter_data: InputListRequestData) => {
  try {
    const { data } = await axios.post(`/api/walrus/v1/project/${project_string_id}/input/view/list`, filter_data)
    return [data.input_list, null]
  } catch(e) {
    return [null, e]

  }
}
