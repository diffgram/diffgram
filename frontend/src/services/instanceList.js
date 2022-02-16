import axios from './customInstance/customInstance'

export const postInstanceList = async (url, instance_list) => {
    try {
        const { data } = await axios.post(
            url, 
            { 
                instance_list,
                and_complete: false    
            }
        )
        return data
    } catch(e) {
        return null
    }
}

export const getInstanceList = async (url, payload = {}) => {
    try {
        const { data: { file_serialized: { instance_list } } } = await axios.post(url, payload)
        const new_list = instance_list.filter(instance => {
            if (instance.type !== "relation") return true
            if (instance.from_instance_id && instance.to_instance_id) return true
        })
        return new_list
    } catch (e) {
        return null
    }
}