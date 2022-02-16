import axios from './customInstance/customInstance'

export const getProjectList = async () => {
    const response = await axios.post("/api/v1/project/list", {})
    return response
}