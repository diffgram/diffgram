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

  private generate_grouped_by_label_format(report : Report){
    // this is similar to generate_second_group_user_format()
    // some assumption are different, e.g. labelNamesMap is a dict not a list
 
    this.csv_content = "data:text/csv;charset=utf-8,";
    this.csv_content += 'Date,'

    // header
    console.log(report)
    for(const [i, schema_label] of Object.entries(report.schema.labelNamesMap)){
      this.csv_content += `${schema_label},`
    }

    this.csv_content = this.csv_content.slice(0, -1); // Remove trailing ","
    this.csv_content += '\r\n'

    // assumes that each row is a label / date

    for (const [ii, label] of report.labels.entries()) {

      let row = `${label},`

      for(const [schema_id, schema_label] of Object.entries(report.schema.labelNamesMap)){

        let did_write = false

        for (const [k, tuple] of report.list_tuples_by_period.entries()) { 
          if (label == tuple[0] && schema_id == tuple[2]) {
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
      return this.generate_grouped_by_label_format(this.report)
    }
    else{
      return this.standard_csv_format(this.report)
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


  private standard_csv_format(report){

    this.csv_content = "data:text/csv;charset=utf-8,";

    let headers_metadata = this.append_metadata_headers(this.csv_content)
    if(headers_metadata){
      this.csv_content += headers_metadata
      this.csv_content += ',Label,Value';
    } else{
      this.csv_content += 'Label,Value';
    }

    this.csv_content += '\r\n'

    for (const [i, label] of report.labels.entries()) {

      let row = `${label},`
      let existing_data = false
      for (const [j, tuple] of report.list_tuples_by_period.entries()) { 
        if (label == tuple[0]) {
          row += `${tuple[1]},`
          existing_data = true
        }

      }
      if (!existing_data) {
        row += `${0},`
      }

      this.csv_content += `${row}\r\n`
    }


    return  this.csv_content
  }
  public get_csv_data(): string{
    return this.determine_format_to_generate();
  }



}
