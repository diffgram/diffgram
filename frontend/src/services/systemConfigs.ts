import axios from './customInstance'
import {SystemConfig} from "../types/system_configs/SystemConfig";


export const get_system_logo = async (): Promise<SystemConfig[]> => {
  let url = `/api/v1/system/logo`
  try {
    const response = await axios.get(url)

    return [response.data.logo, null]
  } catch(e) {
    console.error(e)
    return [null, e]
  }
}
