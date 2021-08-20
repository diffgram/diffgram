

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
  private validate_export_obj(){
    let result = true;
    const export_obj = this.export_raw_obj;
    console.log('EXPORT', export_obj)
    // Check existence of metadata fields
    for(const key of this.metadata_keys){
      if(!export_obj[key]){
        throw new Error(`Invalid Export Format: "${key}" key is missing`)
      }
    }
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
