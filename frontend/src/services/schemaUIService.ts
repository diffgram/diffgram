import { SchemaUIExport } from '../helpers/interfaces/genaral/SchemaUI'
import axios from './customInstance'

export const create_new_schema_ui = async (project_string_id: string, payload: SchemaUIExport) => {
    try {
        const result = await axios.post(`/api/v1/project/${project_string_id}/ui_schema/new`, payload)
        return result
    } catch(e) {
        throw e
    }
}