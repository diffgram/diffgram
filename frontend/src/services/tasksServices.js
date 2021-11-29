import axios from "axios";

export const nextTask = async job_id => {
  try {
    const response = await axios.post(`/api/v1/job/${job_id}/task/next`, {});
    return response;
  } catch (e) {
    return {
      status: 400,
      data: {}
    };
  }
};

export const submitTaskReview = async (task_id, payload) => {
  try {
    const response = await axios.post(
      `/api/v1/task/${task_id}/review`,
      payload
    );
    return response;
  } catch (e) {
    return {};
  }
};

export const finishTaskAnnotation = async task_id => {
  try {
    const response = await axios.post(`/api/v1/task/${task_id}/complete`, {});
    return response;
  } catch (e) {
    return {};
  }
};

export const assignUserToTask = async (
  user_id,
  project_string_id,
  task_id,
  relation = "assignee"
) => {
  const response = await axios.post(
    `/api/v1/project/${project_string_id}/task/${task_id}/user/modify`,
    {
      user_id,
      relation
    }
  );

  return response;
};
