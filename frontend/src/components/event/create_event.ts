import axios from "../../services/customAxiosInstance";


export const create_event = async function(project_string_id, event_data){
  try{
    const response = await axios.post(`/api/v1/project/${project_string_id}/event/create`, {
      file_id: event_data.file_id ? parseInt(event_data.file_id, 10) : undefined,
      task_id: event_data.task_id ? parseInt(event_data.task_id, 10): undefined,
      project_string_id: project_string_id,
      object_type: event_data.object_type,
      page_name: event_data.page_name,
      kind: 'user_visit'
    });
    if(response.status === 200){
      return response.data;
    }

  }
  catch (e) {
    console.error(e);
  }
}
