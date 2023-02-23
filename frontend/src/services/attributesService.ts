import axios from './customInstance'
import {AttributeTemplateGroup} from "../types/attributes/AttributeTemplateGroup";

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

export const archive_attribute_group = async (project_string_id, group) => {
  try {
    const payload = {
      group_id: Number(group.id),
      mode: 'ARCHIVE',
      kind: group.kind,
      global_type: group.global_type ? group.global_type : 'file'
    }

    const { data } = await axios.post(`/api/v1/project/${project_string_id}/attribute/group/update`, payload)

    return [data, null]
  } catch(e) {
    return [null, e]
  }
}

export const attribute_group_update = async (project_string_id, mode, group: AttributeTemplateGroup) => {
  try{
    let response = await axios.post(
      `/api/v1/project/${project_string_id}/attribute/group/update`,
      {
        group_id: Number(group.id),
        name: group.name,
        prompt: group.prompt,
        label_file_list: group.label_file_list,
        kind: group.kind,
        default_id: group.default_id,
        default_value: group.default_value,
        is_read_only: group.is_read_only,
        min_value: group.min_value,
        max_value: group.max_value,
        ordinal: group.ordinal,
        mode: mode,
        is_global: group.is_global,
        global_type: group.global_type ? group.global_type : 'file',
      })
    let data = response.data
    return [data, null]

  } catch (e){
    return [null, e]
  }
}
