import axios from './customInstance'

export const getInstanceTemplatesFromProject = async function(project_string_id, schema_id){
  try{
    const response = await axios.post(
      `/api/v1/project/${project_string_id}/instance-template/list`,
      {
        schema_id: schema_id
      }
    );
    return [response.data, null]
  }
  catch (error){
    return [null, error]
  }
}
