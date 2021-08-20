

class DiffgramExportFileIngestor{
  public export_raw_obj: any = null;
  public file: any = null;

  private validate_export_obj(){
    let result = true;
    const export_obj = export_raw_obj;
    if(!export_obj.export_info){
      throw new Error('Invalid Export Format: export_info key is missing')
    }
  }

  public constructor(export_raw_obj, file) {
    this.export_raw_obj = export_raw_obj
    this.file = file
    this.validate_export_obj();
  }


}
