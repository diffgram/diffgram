import {v4 as uuidv4 } from 'uuid'

export class UI_Schema {
  public client_creation_ref_id
  public client_created_time
  public name
  public archived
  public is_visible
  public is_public

  constructor() {
      
  }

  public new(): any {

    this.client_creation_ref_id = uuidv4();
    this.client_created_time = new Date().toISOString();
    this.name = "Untitled";
    this.archived = false
    this.is_visible = true
    this.is_public = false

  }

  public serialize(): any {
    return JSON.stringify(this)
  }

  public copy(old): any {

    // TODO reivew in new class context

    let ui_schema = {...old}
    ui_schema.external_src_list = [...old.external_src_list]
    ui_schema.client_creation_ref_id = uuidv4();
    ui_schema.client_created_time = new Date().toISOString();
    ui_schema.name = "Copy of " + old.name
    ui_schema.is_public = false
    return ui_schema

  }

}
