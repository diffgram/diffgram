import axios from "axios";


export const get_child_exams = async (project_string_id, exam_id) => {
  try {
    let url = `/api/v1/job/list`;
    const {data} = await axios.post(url, {...metadata})
    return data
  } catch (e) {
    console.error(e)
    return undefined
  }
}
