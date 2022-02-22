import axios from './customInstance'

export const getProjectList = async () => {
    const response = await axios.post("/api/v1/project/list", {})
    return response
}

export const getProject = async (project_string_id) => {
  try{
    const response = await axios.get(`/api/project/${project_string_id}/view`)
    return [response.data, null]
  }
  catch (e){
    return [null, e]
  }

}
