import axios from './customInstance'

export const getLabelboxProjectList = async (connection_id) => {
    let url = `/api/walrus/v1/connectors/${connection_id}/fetch-data`
    try {
        const { data } = await axios.post(
            url,
            {
              opts:{
                action_type: 'get_project_list'
              }
            }
        )
        return [data, null]
    } catch(e) {
        console.error(e)
        return [null, e]
    }
}
