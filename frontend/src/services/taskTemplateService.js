import axios from './customInstance'

export const get_task_template_details = async (task_template_id) => {

  try{
    const response = await axios.post(`/api/v1/job/${task_template_id}/builder/info`, {
      mode_data: 'job_detail',
    })
    if (response.data.log.success == true) {
      let exam = response.data.job;
      return exam
    }
  }
  catch (e){
    console.error(e);
  }
}

export const update_task_template = async (project_string_id, task_template_id, task_template) => {

  try{
    const response = await axios.post(
      `/api/v1/project/${project_string_id}/job/update`,
      {
        ...task_template,
        job_id: task_template_id,
      }
    );
    if(response.status === 200){
      return [response.data, null]
    }
  }
  catch (e){
    return [null, e]
  }
}


export const get_task_template_credentials = async (metadata) => {

  try{
    const response = await axios.post(`/api/v1/credential/list`, {
      metadata: metadata
    })
    if (response.status === 200) {
      let credential_list = response.data.credential_list;
      return credential_list
    }
  }
  catch (e){
    console.error(e);
  }
}


export const archive_task_template = async (job_id, job_list, mode) => {
  try{
    let response = await axios.post("/api/v1/job/cancel", {
        job_id: job_id,
        job_list: job_list,
        mode: mode,
      })
    if (response.data.log.success == true) {
      return [true, null]
    }

    return [false, null]
  }
  catch (e){
    return[null, e]
  }
}

export const get_task_template_members = async (job_id) => {
  try{
    let response = await axios.get(`/api/v1/job/${job_id}/members-list`, {})
    if (response.status === 200) {
      return [response.data, null]
    }

    return [false, null]
  }
  catch (e){
    return[null, e]
  }
}
