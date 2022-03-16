import axios from './customInstance'

export const is_mailgun_set = async () => {
    try {
        const { data } = await axios.get('/api/configs/is-mailer-set')
        return data
    } catch(e) {
        return {
            mailgun: false
        }
    }
}

export const get_install_info = async () => {
    try {
        const { data } = await axios.get('/api/v1/admin/install/info')
        return data
    } catch(error) {
        return {
            error
        }
    }
}


export const is_open_source = async () => {
  try {
    const { data } = await axios.get('/api/configs/is-open-source')
    return [data, null]
  } catch(e) {
    return [null, e]

  }
}
