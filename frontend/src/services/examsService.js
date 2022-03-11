import axios from './customInstance'

export const get_examinations = async (project_string_id, exam_id, mode) => {
  try {
    let url = `/api/v1/job/list`;
    const {data} = await axios.post(url, {
      metadata: {
        project_string_id: project_string_id,
        parent_id: exam_id,
        type: 'examination',
        builder_or_trainer: {
          mode: mode
        }
      }
    })
    return data.Job_list
  } catch (e) {
    console.error(e)
    return undefined
  }
}


export const exam_start_apply = async (exam_id) => {
  try {
    const response = await axios.post('/api/v1/task-template/apply',
      {
        'task_template_id': parseInt(exam_id, 10)
      })
    if (response.data.log.success == true) {
      return [response.data, undefined]
    }
    else{
      return [null, null];
    }
  } catch (e) {
    console.error(e)
    return [undefined, e]
  }
}


export const exam_pass = async (exam_id) => {
  try {
    const response = await axios.post('/api/v1/exam/pass',
      {
        job_id: parseInt(exam_id, 10)
      })
    if (response.data.log.success == true) {

      return [true, null]

    }
  } catch (e) {
    console.error(e)
    return [undefined, e]
  }
}

