import axios from 'axios'

export const getJobStats = async (job_id) => {
    const { data } = await axios.get(`/api/job/${job_id}/stat`)
    return data
}

export const getJobStatsForUser = async (job_id, user_id) => {
    const { data } = await axios.get(`/api/job/${job_id}/user/${user_id}/stats`)
    return data
}