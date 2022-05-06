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
  let url = `/api/v1/project/${project_string_id}/actions/workflow/${workflow_id}/action`;
  try {
    const {data} = await axios.post(
      url,
      {
        public_name: action.public_name,
        kind: action.kind,
        description: action.description,
        workflow_id: workflow_id,
        trigger_data: action.trigger_data,
        condition_data: action.condition_data,
        completion_condition_data: action.completion_condition_data,
        action_template_id: action.action_template_id,
        icon: action.icon,
      }
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
        workflow_id: workflow_id,
        trigger_data: action.trigger_data,
        condition_data: action.condition_data,
        completion_condition_data: action.completion_condition_data,
        action_template_id: action.action_template_id,
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
        workflow_id: this.workflow.id,
        name: this.workflow.name,
        trigger_type: this.workflow.trigger_type,
        time_window: this.workflow.time_window,
        active: this.flow.active,
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
