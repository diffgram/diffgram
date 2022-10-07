import {v4 as uuidv4 } from 'uuid'
import { SchemaUIExport } from '../../helpers/interfaces/genaral/SchemaUI'
export class UI_Schema implements SchemaUIExport {
  public client_creation_ref_id: string
  public client_created_time: string
  public name: string
  public archived: boolean
  public is_visible: boolean
  public is_public: boolean

  public new(): void {
    this.client_creation_ref_id = uuidv4();
    this.client_created_time = new Date().toISOString();
    this.name = "Untitled";
    this.archived = false
    this.is_visible = true
    this.is_public = false
  }

  public export(): SchemaUIExport {
    const ui_schema_object: SchemaUIExport = {
      client_creation_ref_id: this.client_creation_ref_id,
      client_created_time: this.client_created_time,
      name: this.name,
      archived: this.archived,
      is_visible: this.is_visible,
      is_public: this.is_public
    }

    return ui_schema_object
  }

  public copy(old): any {

    // TODO reivew in new class context

    let ui_schema = {...old}
    ui_schema.client_creation_ref_id = uuidv4();
    ui_schema.client_created_time = new Date().toISOString();
    ui_schema.name = "Copy of " + old.name
    ui_schema.is_public = false
    return ui_schema

  }

}
