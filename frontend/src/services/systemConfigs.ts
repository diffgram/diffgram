import axios from './customInstance'
import {SystemConfig} from "../types/system_configs/SystemConfig";
import {Image} from "../types/files";


export const get_system_logo = async (): Promise<[Image, Error]> => {
  let url = `/api/v1/system/logo`
  try {
    const response = await axios.get(url)
    let image = response.data.logo_data as Image
    return [image, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}

export const upload_system_logo = async (file): Promise<[SystemConfig, Error]> => {
  const formData = new FormData();
  formData.append('file', file);
  let url = `/api/v1/admin/set-logo`
  try {
    const response = await axios.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return [response.data.logo_data, null]
  } catch (e) {
    console.error(e)
    return [null, e]
  }
}
