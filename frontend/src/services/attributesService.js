import axios from './customInstance'

export const attribute_update_or_new = async (mode, project_string_id, attribute) => {
    try {
        const { data } = await axios.post(`/api/v1/project/${project_string_id}/attribute`, { mode, attribute })
        return {
            status: 200,
            data,
            error: {}
        }
    } catch(error) {
        return {
            status: error.response.status,
            data: null,
            error: error.response.data.log.error
        }
    }
}

export const attribute_group_list = async (project_string_id,
                                           group_id,
                                           schema_id,
                                           mode,
                                           group_id_list = undefined,
                                           with_labels = false) => {
  let url =  `/api/v1/project/${project_string_id}/attribute/template/list`
  try {
    const { data } = await axios.post(
      url,
      {
        group_id: group_id,
        mode: mode,
        group_id_list: group_id_list,
        with_labels: with_labels,
        schema_id: schema_id
      }
    )
    return [data, null]
  } catch(e) {
    console.error(e)
    return [null, e]
  }
}
