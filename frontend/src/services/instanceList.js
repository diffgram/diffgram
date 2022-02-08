import axios from "axios";

export const postInstanceList = async (project_string_id, file_id, instance_list) => {
    try {
        const { data } = await axios.post(
            `/api/project/${project_string_id}/file/${file_id}/annotation/update`, 
            { instance_list }
        )
        return data
    } catch(e) {
        return null
    }
}

export const getInstanceList = async (project_string_id, file_id) => {
    try {
        const { data: { file_serialized: { instance_list } } } = await axios.post(`/api/project/${project_string_id}/file/${file_id}/annotation/list`, {})
        const new_list = instance_list.filter(instance => {
            if (instance.type !== "relation") return true
            if (instance.from_instance_id && instance.to_instance_id) return true
        })
        return new_list
    } catch (e) {
        return null
    }
}