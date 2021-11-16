import axios from "axios"

export const nextTask = async (job_id) => {
    try {
        const response = await axios.post(
            `/api/v1/job/${job_id}/task/next`,
            {}
        );
        return response
    } catch(e) {
        console.log(e)
        return {
            status: 400,
            data: {}
        }
    }
}