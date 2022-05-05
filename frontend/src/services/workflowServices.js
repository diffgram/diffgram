import axios from "@/services/customInstance";

export const new_workflow = async (project_string_id, workflow) => {
  let url = `/api/v1/project/${this.project_string_id}/actions/workflow/new`;
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
  let url = `/api/v1/project/${this.project_string_id}/actions/workflow/update`;
  try {
    const {data} = await axios.post(
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
  let url = `/api/v1/project/${project_string_id}/flow/${workflow_id}`;
  try {
    const {data} = await axios.get(
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
