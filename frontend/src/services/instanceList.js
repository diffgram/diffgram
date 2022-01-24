import axios from "axios";

export const postInstanceList = async (project_string_id, file_id, instance_list) => {
    try {
        const { data } = await axios.post(
            `/api/project/${project_string_id}/file/${file_id}/annotation/update`, 
            { instance_list }
        )
        return data
    } catch(e) {
        console.log(e)
        return null
    }
}