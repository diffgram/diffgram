import axios from './customInstance'


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

export const getFollowingTask = async (project_string_id, task_id, job_id, direction, assign_to_user = false) => {
  try {
    const payload = {
      project_string_id,
      task_id,
      direction,
      assign_to_user
    }

    const response = await axios.post(`/api/v1/job/${job_id}/next-task`, payload)
    
    return [response.data, null]
  } catch(e) {
    return [null, e]
  }
}

export const deferTask = async payload => {
  try {
    const { data } = await axios.post('/api/v1/task/update', payload)
    return data
  } catch(e) {
    return {}
  }
}

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
  try {
    const response = await axios.post(
      `/api/v1/project/${project_string_id}/task/${task_id}/user/modify`,
      {
        user_id,
        relation
      }
    );
    return response;
  } catch (e) {
    return {};
  }
};

export const batchAssignUserToTask = async (
  user_id_list,
  project_string_id,
  tasks,
  relation = "assignee"
) => {
  try {
    const requests = tasks.map(task =>
      axios.post(
        `/api/v1/project/${project_string_id}/task/${task.id}/user/add`,
        {
          user_id_list,
          relation
        }
      )
    );

    const responses = await axios.all(requests);
    return responses;
  } catch (e) {
    return [];
  }
};

export const batchRemoveUserFromTask = async (
  user_id_list,
  project_string_id,
  tasks,
  relation = "assignee"
) => {
  try {
    const requests = tasks.map(task =>
      axios.post(
        `/api/v1/project/${project_string_id}/task/${task.id}/user/remove`,
        {
          user_id_list,
          relation
        }
      )
    );

    const responses = await axios.all(requests);
    return responses;
  } catch (e) {
    return [];
  }
};

export const trackTimeTask = async (time_spent,
                                    task_id,
                                    status,
                                    job_id,
                                    file_id,
                                    parent_file_id) =>{

  try{
    const response = await axios.post(`/api/v1/task/${task_id}/track-time`, {
      status: status,
      time_spent: time_spent,
      job_id: job_id,
      file_id: file_id,
      parent_file_id: parent_file_id
    })
    if(response.status === 200){
      return [response.data, null]
    }
    else{
      return [null, response]
    }

  }
  catch (e){
    return [null, e]
  }
}
