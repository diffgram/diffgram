import axios from "axios"
import { logout } from "../userServices"

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
