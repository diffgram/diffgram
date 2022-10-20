import axios from './customInstance'
import {File} from '../types/files'
import { RequestResponse } from '../types/request'

export const get_file_list = async (project_string_id, user_name, metadata) => {
  let url = `/api/project/${project_string_id}/user/${user_name}/file/list`
  try {
    const response = await axios.post(
      url,
      {
        metadata: metadata,
        project_string_id: project_string_id
      }
    )
    if (response.data['file_list'] != null) {
      return [response.data , null];
    }
    return [response, null]
  } catch(e) {
    console.error(e)
    return [null, e]
  }
}

export const get_file_signed_url = async (project_string_id, file_id) => {
  let url = `/api/project/${project_string_id}/file/${file_id}/get-signed-url`
  try {
    const response = await axios.get(url)

    return [response.data, null]
  } catch(e) {
    console.error(e)
    return [null, e]
  }
}

export const get_child_files = async (project_string_id: string, parent_file_id: number): Promise<RequestResponse<File[]>> => {
  let url = `/api/v1/project/${project_string_id}/file/${parent_file_id}/child-files`
  try {
    const { data } = await axios.get(url)

    return {
      result: data.child_files,
      error: null
    }

  } catch(e) {
    return {
      result: null,
      error: e
    }
  }
}
