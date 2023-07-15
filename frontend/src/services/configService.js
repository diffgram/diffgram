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

export const is_oauth2_set = async () => {
  try {
    const { data } = await axios.get('/api/configs/is-oauth2-set')
    return data
  } catch(e) {
    return {
      use_oauth2: false
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

export const get_queue_status = async () => {
    try {
        const { data } = await axios.get('/api/v1/admin/queue/status')
        return data
    } catch(error) {
        return {
            error
        }
    }
}

export const get_walrus_status = async () => {
    try {
        return await axios.get('/api/walrus/status')
    } catch(error) {
        return error
    }
}

export const get_default_status = async () => {
    try {
        return await axios.get('/api/status')
    } catch(error) {
        return error
    }
}


// or $store.commit('check_is_open_source') and $store.state.system.is_open_source
export const is_open_source = async () => {
  try {
    const { data } = await axios.get('/api/configs/is-open-source')
    return [data, null]
  } catch(e) {
    return [null, e]

  }
}

export const get_large_api_chunk_size = async () => {
  try {
    let res = await axios.get('/api/configs/large-api-chunk-size')
    return res.data.large_api_chunk_size
  } catch(error) {
    return error
  }
}

export const get_version = async () => {
  try {
    let res = await axios.get('/api/configs/version')
    return res.data
  } catch(error) {
    return error
  }
}
