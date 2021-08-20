

export default class DiffgramExportFileIngestor{
  public export_raw_obj: any = null;
  public file: any = null;
  private export_ingestor_version: string = '1.0' // This is the ingestor for format v1.0
  public metadata_keys: string[] = ['readme', 'label_map', 'export_info', 'attribute_groups_reference']

  public constructor(export_raw_obj, file) {
    this.export_raw_obj = export_raw_obj
    this.file = file
    this.validate_export_obj();
  }
  public get_label_names(){
    const export_obj = this.export_raw_obj;
    const result = [];
    if(!export_obj.label_map){
      throw new Error('Export data has no key "labels_map". Please provide this key in the JSON file.')
    }
    for(const key of Object.keys(export_obj.label_map)){
      let label_name = export_obj.label_map[key]
      result.push(label_name)
    }
    return result;
  }
  public get_file_names(){
    const export_obj = this.export_raw_obj;
    const result = [];
    for(const key of Object.keys(export_obj)){
      if(this.metadata_keys.includes(key)){
        continue
      }
      let file_data = export_obj[key];
      if(!file_data.file || !file_data.file.original_filename){
        throw new Error(`File key ${key} has no "file.original_filename". Please check this key exists in the export.`)
      }
      result.push(file_data.original_filename)

    }
    return result;
  }

  public get_blob_list(){
    const export_obj = this.export_raw_obj;
    const result = [];
    for(const key of Object.keys(export_obj)){
      if(this.metadata_keys.includes(key)){
        continue
      }
      let file_data = export_obj[key];
      if(!file_data.file || !file_data.file.blob_url){
        throw new Error(`File key ${key} has no blob. Please check this file has the key "file.blob_url" in the export.`)
      }
      result.push(file_data.file.blob_url)

    }
    return result;
  }

  public check_export_meta_data(){
    // Check existence of metadata fields
    const result = [];
    const export_obj = this.export_raw_obj;
    for(const key of this.metadata_keys){
      if(!export_obj[key]){
        throw new Error(`Invalid Export Format: "${key}" key is missing`)
      }
    }
  }

  private validate_export_obj(){
    let result = true;
    const export_obj = this.export_raw_obj;
    this.check_export_meta_data()
    // Check valid file keys
    const file_keys = Object.keys(this.export_raw_obj).filter(key => !this.metadata_keys.includes(key));
    for(const file_key of file_keys){
      let file_id = parseInt(file_key, 10);
      if(isNaN(file_id)){
        throw new Error(`Invalid Export Format: "${file_key}" unrecognized key.`)
      }
    }

  }

}
