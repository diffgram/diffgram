import axios from './customInstance'

export const start_project_migration = async (project_string_id, project_migration_data) => {

  try {
    const response = await axios.post(
      `/api/walrus/project-migration/${project_string_id}/new`,
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
