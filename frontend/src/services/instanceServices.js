import axios from './customInstance/customInstance'

export const get_instance_list_from_file = async (project_string_id, file_id) => {
  try {
    let url = `/api/project/${project_string_id}/file/${file_id}/annotation/list`;
    const { data } = await axios.post(url, {})
    return data
  } catch(e) {
    return {
      completed: 0,
      total: 0
    }
  }
}


export const get_instance_list_from_task = async (project_string_id, task_id) => {
  try {
    const { data } = await axios.get(`/api/v1/task/${task_id}/annotation/list`)
    return data
  } catch(e) {
    return {
      completed: 0,
      total: 0
    }
  }
}

