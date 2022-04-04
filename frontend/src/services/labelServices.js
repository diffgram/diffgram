import axios from "@/services/customInstance";


export const get_labels = async (project_id, schema_id = undefined) => {
  try {
    const response = await axios.get(
      `'/api/project/'${project_string_id}/labels/refresh`,
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
