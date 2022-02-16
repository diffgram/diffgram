import axios from './customInstance/customInstance'

export const mockAnnotations = async (project_string_id) => {
    
    try {
        const response = await axios.post(
            `/api/walrus/v1/project/${project_string_id}/gen-data`,
            {
              'data_type' : 'annotations'
              }
        );
        return response
    } catch(e) {
        console.log(e)
    }
}
