import axios from './customInstance'

export const start_project_migration = async (project_string_id, project_migration_data) => {

  try {
    const response = await axios.post(
      `/api/walrus/project/${project_string_id}/project-migration/new`,
      {
        labelbox_project_id: project_migration_data.labelbox_project_id,
        connection_id: project_migration_data.connection.id,
        ...project_migration_data
      }
    );
    return [response.data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}


export const get_project_migration = async (project_string_id, project_migration_id) => {

  try {
    const response = await axios.get(
      `/api/walrus/project/${project_string_id}/project-migration/${project_migration_id}`,
      {
        project_migration_id: project_migration_id
      }
    );
    return [response.data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}


export const get_project_migration_list = async (project_string_id) => {

  try {
    const response = await axios.get(
      `/api/walrus/project/${project_string_id}/project-migration/list`,
      {}
    );
    return [response.data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}
