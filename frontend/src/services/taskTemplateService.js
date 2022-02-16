import axios from './customInstance/customInstance'

export const get_task_template_details = async (exam_id) => {

  try{
    const response = await axios.post(`/api/v1/job/${exam_id}/builder/info`, {
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
