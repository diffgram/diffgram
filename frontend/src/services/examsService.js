import axios from "axios";


export const get_child_exams = async (project_string_id, exam_id) => {
  try {
    let url = `/api/v1/job/list`;
    const {data} = await axios.post(url, {
      metadata: {
        project_string_id: project_string_id,
        parent_id: exam_id,
      }
    })
    return data
  } catch (e) {
    console.error(e)
    return undefined
  }
}


export const exam_start_apply = async (exam_id) => {
  try {
    const response = await axios.post('/api/v1/job/apply',
      {
        'job_id': exam_id
      })
    if (response.data.log.success == true) {
      return response.data
    }
    else{
      return undefined;
    }
  } catch (e) {
    console.error(e)
  }
}
