import axios from './customInstance'

export const runReport = async (project_string_id: string, report_template_id: number = undefined, report_template_data: any) =>{

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


export const getReportTemplate = async (project_string_id: string, report_template_id: number) =>{

  try{
    const response = await axios.get(`/api/v1/project/${project_string_id}/report/${report_template_id}`, {})
    if(response.status === 200){
      return [response.data.report_template, null]
    }
    else{
      return [null, response]
    }

  }
  catch (e){
    return [null, e]
  }
}
