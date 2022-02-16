import axios from './customInstance/customInstance'

export const runReport = async (project_string_id, report_template_id = undefined, report_template_data) =>{

  try{
    const response = await axios.post(`/api/v1/report/run`, {
      project_string_id: project_string_id,
      report_template_id: report_template_id,
      report_template_data: report_template_data,
    })
    if(response.status === 200){
      return [response.data, null]
    }
    else{
      return [null, response]
    }

  }
  catch (e){
    return [null, e]
  }
}
