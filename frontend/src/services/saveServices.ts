import axios from "./customInstance"

export const saveTaskAnnotations = async (task_id: number, payload: Object) => {
  try {
    const response = await axios.post(`/api/v1/task/${task_id}/annotation/update`, payload)
    return [response.data, null]
  }
  catch(e) {
    return [null, e]
  }
}

export const saveFileAnnotations = async (project_string_id: string, file_id: number, payload: Object) => {
  try {
    const response = await axios.post(`/api/project/${project_string_id}/file/${file_id}/annotation/update`, payload)
    return [response.data, null]
  }
  catch(e) {
    return [null, e]
  }
}