import axios from './customInstance'

export const get_action_stat = async (project_string_id, action_id) => {
    try {
        const { data } = await axios.get(`/api/v1/project/${project_string_id}/action/${action_id}`)
        console.log(data)
        return data
    } catch(e) {
        return null
    }
}