import axios from "./customInstance";

export const get_dataset_list = async (project_string_id) => {
  try {
    const { data } = await axios.post(`/api/v1/project/${project_string_id}/directory/list`, {})
    let directory_list = data.directory_list;
    for (let elm of directory_list){
      console.log(elm.nickname)
    }
    return [directory_list, null]
  } catch(e) {
    return [null, e]

  }
}

export const create_new_dataset = async (project_string_id, nickname) => {
  try {
    const payload = {
      nickname,
      access_type: 'project'
    }
    const { data } = await axios.post(`/api/v1/project/${project_string_id}/directory/new`, payload)

    const result = {
      success: data.log.success,
      new_directory: data.new_directory
    }

    return [result, null]
  } catch(e) {
    return [null, e]
  }
}

export const update_dataset = async (project_string_id, current_directory, mode) => {
  try {
    const payload = {
      nickname: current_directory.nickname,
      directory_id: current_directory.directory_id,
      mode: mode,
      access_type: 'project'
    }

    const { data } = await axios.post(`/api/v1/project/${project_string_id}/directory/update`, payload)

    const result = {
      success: data.log.success,
      directory_list: data.project.directory_list
    }

    return [result, null]
  } catch(e) {
    return [null, e]
  }
}

export const refresh_dataset_list = async (project_string_id, payload) => {
  try {
    const { data } = await axios.post(`/api/v1/project/${project_string_id}/directory/list`, payload)

    return [data, null]
  } catch(e) {
    return [null, e]
  }
}
