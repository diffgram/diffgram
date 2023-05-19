import axios from "./customInstance";


export const get_mongo_database_list = async (connection_id: number) => {
  let url = `/api/walrus/v1/connectors/${connection_id}/fetch-data`
  try {
    const { data } = await axios.post(
      url,
      {
        opts:{
          action_type: 'get_db_list',
        }
      }
    )
    return [data, null]
  } catch(e) {
    console.error(e)
    return [null, e]
  }
}

export const get_mongo_collections_list = async (connection_id: number, db_name: string) => {
  let url = `/api/walrus/v1/connectors/${connection_id}/fetch-data`
  try {
    const { data } = await axios.post(
      url,
      {
        opts:{
          action_type: 'list_collections_from_db',
          db_name: db_name
        }
      }
    )
    return [data, null]
  } catch(e) {
    console.error(e)
    return [null, e]
  }
}
