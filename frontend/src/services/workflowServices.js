import axios from "@/services/customInstance";

export const action_template_list = async (project_string_id, workflow_id, action) => {
  let url = `/api/v1/project/${project_string_id}/action-template/list`;
  try {
    const {data} = await axios.get(url)
    return [data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}


export const action_update = async (project_string_id, workflow_id, action) => {
  let url = `/api/v1/project/${project_string_id}/actions/${action.id}`;
  let req_data = {
    ...action,
    workflow_id: workflow_id
  }
  try {
    console.log('action', action);
    console.log('req_data', req_data);
    const {data} = await axios.put(
      url,
      req_data
    )
    return [data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}

export const action_manual_trigger = async (project_string_id, action) => {
  let url = `/api/v1/project/${project_string_id}/actions/${action.id}/manual_trigger`;
  let req_data = {
    ...action
  }
  try {
    const {data} = await axios.put(
      url,
      req_data
    )
    return [data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}

export const new_action = async (project_string_id, workflow_id, action) => {
  let url = `/api/v1/project/${project_string_id}/actions/workflow/${workflow_id}/action`;
  try {
    const {data} = await axios.post(
      url,
      {
        public_name: action.public_name,
        kind: action.kind,
        description: action.description,
        ordinal: action.ordinal,
        workflow_id: workflow_id,
        trigger_data: action.trigger_data,
        condition_data: action.condition_data,
        completion_condition_data: action.completion_condition_data,
        template_id: action.template_id,
        icon: action.icon,
      }
    )
    return [data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}

export const new_workflow = async (project_string_id, workflow) => {
  let url = `/api/v1/project/${project_string_id}/actions/workflow/new`;
  try {
    const {data} = await axios.post(
      url,
      {
        name: workflow.name,
        trigger_type: workflow.trigger_type,
        time_window: workflow.time_window
      }
    )
    return [data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}

export const workflow_update = async (project_string_id, workflow, mode) => {
  let url = `/api/v1/project/${project_string_id}/actions/workflow/update`;
  try {
    const {data} = await axios.put(
      url,
      {
        workflow_id: workflow.id,
        name: workflow.name,
        trigger_type: workflow.trigger_type,
        time_window: workflow.time_window,
        active: workflow.active,
        mode: mode

      }
    )
    return [data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}

export const get_workflow = async (project_string_id, workflow_id) => {
  let url = `/api/v1/project/${project_string_id}/workflow/${workflow_id}`;
  try {
    const {data} = await axios.get(url)
    return [data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}

export const get_action_template = async (project_string_id, action_template_id) => {
  let url = `/api/v1/project/${project_string_id}/action-template/${action_template_id}`;
  try {
    const {data} = await axios.get(url)
    return [data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}
