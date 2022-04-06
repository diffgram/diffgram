import axios from "@/services/customInstance";


export const get_labels = async (project_string_id, schema_id = undefined) => {
  try {
    const response = await axios.get(
      `/api/project/${project_string_id}/labels`,
      {
        params:{
          schema_id: schema_id
        }
      }
    );
    return [response.data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}

export const get_schemas = async (project_string_id) => {
  try {
    const response = await axios.get(
      `/api/v1/project/${project_string_id}/labels-schema`,
      {
        params:{}
      }
    );
    return [response.data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}
