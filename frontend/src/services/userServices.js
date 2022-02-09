import axios from "axios";


export const user_has_credentials = async (project_string_id, user_id, task_template_id) => {

  try{
    const response = await axios.get(`/api/v1/project/${project_string_id}/user/${user_id}/has-credentials`, {
      params:{
        task_template_id: task_template_id
      }
    })
    if (response.status === 200) {
      return [response.data, null]
    }
    else{
      return [null, response]
    }
  }
  catch (e){
    console.error(e);
    return [null, e]
  }
}
