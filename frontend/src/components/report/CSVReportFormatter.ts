import { ReportTemplate } from '@/types/ReportTemplate'
import { Report } from '@/types/Report'

export class CSVReportFormatter{
  public report: Report = null;
  public report_template: ReportTemplate = null;
  public csv_content: string = '';

  public constructor(
      report : Report,
      report_template: ReportTemplate) {

    this.csv_content = ''
    this.report = report
    this.report_template = report_template
  }

  private generate_grouped_by_label_format(){
    this.csv_content = "data:text/csv;charset=utf-8,";
    this.csv_content += 'File ID,'
    const label_names = []
    /*
    for(const elm of this.report.second_grouping){
      if(!label_names.includes(this.label_names_map[elm])){
        label_names.push(this.label_names_map[elm])
        this.csv_content += `${this.label_names_map[elm]},`
      }
    }
    */
    this.csv_content = this.csv_content.slice(0, -1); // Remove trailing ","
    this.csv_content += '\r\n'
    let file_label_map = {}

    for(let i = 0; i < this.report.values.length ; i++){
      const file_id = this.report.labels[i];
      const count = this.report.values[i];
      const label_name = this.report.second_grouping[i];
      if(file_label_map[file_id]){
        file_label_map[file_id][label_name] = count
      }
      else{
        file_label_map[file_id] = {[label_name]: count}
      }

    }

    for(let file_id of Object.keys(file_label_map)){
      let row = `${file_id},`;
      let labels_count = label_names.map(elm => 0);

      /*
      for(let label_file_id of Object.keys(file_label_map[file_id])){
        let index = label_names.indexOf(this.label_names_map[label_file_id]);
        labels_count[index] = file_label_map[file_id][label_file_id]
      }
      */

      for(let i = 0; i < labels_count.length; i++){
        let current = labels_count[i];
        if(i != labels_count.length - 1){
          row += `${current},`
        }
        else{
          row += `${current}`
        }
      }
      this.csv_content += `${row}\r\n`

    }
    return this.csv_content
  }

  private generate_second_group_user_format(report : Report){

    this.csv_content = "data:text/csv;charset=utf-8,";
    this.csv_content += 'Date,'

    // header
    for(const [i, tuple] of report.user_metadata.entries()){
      this.csv_content += `${tuple.name},`
    }

    this.csv_content = this.csv_content.slice(0, -1); // Remove trailing ","
    this.csv_content += '\r\n'

    // assumes that each row is a label / date

    for (const [ii, label] of report.labels.entries()) {

      let row = `${label},`

      for(const [j, user] of report.user_metadata.entries()){

        let did_write = false

        for (const [k, tuple] of report.list_tuples_by_period.entries()) { 
          if (label == tuple[0] && user.member_id == tuple[2]) {
            // write data
            row += `${tuple[1]},`
            did_write = true

          }
        }

        if (did_write == false) {
          // write empty data
          row += `${0},`
        }

      }

      this.csv_content += `${row}\r\n`
    }

    return this.csv_content

  }

  private determine_format_to_generate(){
    /*
    * Depending on report_template config, we can adapt formatting and call different CSV formatting
    * functions. This function returns a function with the appropriate format based on report_template.
    * */
    if(this.report_template.second_group_by == 'user'){
      return this.generate_second_group_user_format(this.report)
    }

    if(this.report_template.second_group_by == 'label'){
      return this.generate_grouped_by_label_format()
    }
    else{
      return this.standard_csv_format()
    }

  }
  private append_metadata_headers(csv_str: string){
    if(!this.report.user_metadata || !this.report.user_metadata[0]){
      return null
    }
    let result = '';
    for(let i = 0;  i < Object.keys(this.report.user_metadata[0]).length; i++){
      let elm = Object.keys(this.report.user_metadata[0])[i]
      result += `${elm}`
      if(i < Object.keys(this.report.user_metadata[0]).length - 1){
        result += ','
      }

    }
    return result
  }

  private append_values(
      values: any[],
      index: number){

    if(!values || values.length == 0){
      return null
    }

    let result = ''
    const value_element = values[index]
    const row_keys = Object.keys(value_element)

    row_keys.map(
      ( key: string,
        key_index: number) => {

      const value = value_element[key]

      result += `${value}`
 
      if (key_index != row_keys.length - 1) result += ','
    })
    return result
  }

  private standard_csv_format(){

    this.csv_content = "data:text/csv;charset=utf-8,";

    let headers_metadata = this.append_metadata_headers(this.csv_content)
    if(headers_metadata){
      this.csv_content += headers_metadata
      this.csv_content += ',Label,Value';
    } else{
      this.csv_content += 'Label,Value';
    }


    this.csv_content += '\r\n'

    let values = undefined
    if (this.report.values && this.report.values.length > 0) {
      values = this.report.values
    } else {
      values = this.report.user_metadata
    }

    for (let i=0; i< this.report.labels.length; i++){
      let content = this.append_values(values, i)
  
      if(content){
        this.csv_content += content + ','
      }
      this.csv_content += `${String(this.report.labels[i]).replace(/,/g, "")},${this.report.values[i]}\r\n`
    }
    return  this.csv_content
  }
  public get_csv_data(): string{
    return this.determine_format_to_generate();
  }



}
