import axios from './customInstance'

export const list_connections = async (project_string_id) => {
    try {
        const { data } = await axios.get(`/api/project/${project_string_id}/connections`, {
          permission_scope: "project",
        })
        return [data.connection_list, null]
    } catch(e) {
        return [null, e]
    }
}
