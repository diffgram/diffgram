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