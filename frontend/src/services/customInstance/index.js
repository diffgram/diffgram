import axios from "axios"
import { logout } from "../userServices"
import router from "../../router/router"
const axiosConfig = {
  baseURL: 'http://127.0.0.1:8085/diffgrampower'
}
const instance = axios.create()

instance.interceptors.response.use(function (response) {
    return response;
  }, async function (error) {
      const { status } = error.response
    if (status === 401) {
        await logout()
    }
    return Promise.reject(error);
  });

export default instance
