import axios from './customAxiosInstance'

export const getJobStats = async (job_id) => {
    try {
        const { data } = await axios.get(`/api/job/${job_id}/stat`)
        return data
    } catch(e) {
        return {
            completed: 0,
            total: 0
        }
    }
}

export const getJobStatsForUser = async (job_id, user_id) => {
    try {
        const { data } = await axios.get(`/api/job/${job_id}/user/${user_id}/stats`)
        return data
    } catch(e) {
        return {
            completed: 0,
            total: 0
        }
    }
}
