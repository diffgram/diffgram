import axios from "axios"

export const nextTask = async (job_id) => {
    try {
        const response = await axios.post(
            `/api/v1/job/${job_id}/task/next`,
            {}
        );
        return response
    } catch(e) {
        return {
            status: 400,
            data: {}
        }
    }
}

export const submitTaskReview = async (task_id, payload) => {
    try{
        const response = await axios.post(`/api/v1/task/${task_id}/review`, payload)
        return response
    } catch(e) {
        return {}
    }
}