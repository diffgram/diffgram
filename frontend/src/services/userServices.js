import axios from './customInstance'
import store from "../store"
import router from "../router/router"


export const user_has_credentials = async (project_string_id, user_id, task_template_id) => {

  try{
    const response = await axios.get(`/api/v1/project/${project_string_id}/user/${user_id}/has-credentials`, {
      params:{
        task_template_id: task_template_id
      }
    })
    if (response.status === 200) {
      return [response.data, null]
    }
    else{
      return [null, response]
    }
  }
  catch (e){
    console.error(e);
    return [null, e]
  }
}

export const logout = async () => {
  try {

    const response = await axios.get('/api/v1/user/logout')

    store.dispatch('log_out')
    if(response.data.url_redirect){
      window.location.replace(response.data.url_redirect)
      return [true, null]
    }
    router.push('/user/login');
    return [true, null]
  } catch(e) {
    console.log(e)
    return [null, e]
  }
}

export const is_user_verified = async () => {
  try {
    return await axios.get('/api/v1/user/verify/is_email_confirmed')
  } catch(e) {
    return e
  }
}
