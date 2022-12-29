
export class CSVReportFormatter{
  public labels: any[] = null;
  public values: number[] = null;
  public second_grouping: any[] = null;
  public values_metadata: any[] = null;
  public label_names_map: object = null;
  public report_template: any = null;
  public csv_content: string = '';

  public constructor(labels: any[],
                     values: number[],
                     second_grouping: number[],
                     label_names_map: object,
                     report_template: object,
                     values_metadata: any[]) {

    this.labels = labels;
    this.values = values;
    this.second_grouping = second_grouping;
    this.label_names_map = label_names_map;
    this.report_template = report_template;
    this.values_metadata = values_metadata;
    this.csv_content = '';
  }

  private generate_grouped_by_label_format(){
    this.csv_content = "data:text/csv;charset=utf-8,";
    this.csv_content += 'File ID,'
    const label_names = []
    for(const elm of this.second_grouping){
      if(!label_names.includes(this.label_names_map[elm])){
        label_names.push(this.label_names_map[elm])
        this.csv_content += `${this.label_names_map[elm]},`
      }
    }
    this.csv_content = this.csv_content.slice(0, -1); // Remove trailing ","
    this.csv_content += '\r\n'
    let file_label_map = {}

    for(let i = 0; i < this.values.length ; i++){
      const file_id = this.labels[i];
      const count = this.values[i];
      const label_name = this.second_grouping[i];
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
      for(let label_file_id of Object.keys(file_label_map[file_id])){
        let index = label_names.indexOf(this.label_names_map[label_file_id]);
        labels_count[index] = file_label_map[file_id][label_file_id]
      }

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
  private determine_format_to_generate(): string{
    /*
    * Depending on report_template config, we can adapt formatting and call different CSV formatting
    * functions. This function returns a function with the appropriate format based on report_template.
    * */
    if(this.report_template.group_by_labels){
      return this.generate_grouped_by_label_format()
    }
    else{
      return this.standard_csv_format()
    }

  }
  private append_metadata_headers(csv_str: string){
    if(!this.values_metadata || !this.values_metadata[0]){
      return null
    }
    let result = '';
    for(let i = 0;  i < Object.keys(this.values_metadata[0]).length; i++){
      let elm = Object.keys(this.values_metadata[0])[i]
      result += `${elm}`
      if(i < Object.keys(this.values_metadata[0]).length - 1){
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
    if (this.values && this.values.length > 0) {
      values = this.values
    } else {
      values = this.values_metadata
    }

    // Add Content from this.stats
    for (let i=0; i< this.labels.length; i++){
      let stats_content = this.append_values(values, i)
  
      if(stats_content){
        this.csv_content += stats_content + ','
      }
      this.csv_content += `${String(this.labels[i]).replace(/,/g, "")},${this.values[i]}\r\n`
    }
    return  this.csv_content
  }
  public get_csv_data(): string{
    return this.determine_format_to_generate();
  }



}
