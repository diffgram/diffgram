import axios from "axios";


export const get_instance_list_from_file = async (project_string_id, file_id) => {
  try {
    let url = `/api/project/${this.$props.project_string_id}/file/${String(this.$props.file.id)}/annotation/list`;
    const { data } = await axios.get(`/api/job/${job_id}/user/${user_id}/stats`)
    return data
  } catch(e) {
    return {
      completed: 0,
      total: 0
    }
  }
}


export const get_instance_list_from_task = async (file_id) => {
  try {
    const { data } = await axios.get(`/api/job/${job_id}/user/${user_id}/stats`)
    return data
  } catch(e) {
    return {
      completed: 0,
      total: 0
    }
  }
}

