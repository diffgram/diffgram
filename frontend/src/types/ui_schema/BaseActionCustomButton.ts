import {CustomButtonWorkflow} from "./CustomButtonWorkflow";


export class BaseActionCustomButton {
  metadata: object
  type: string
  name: string
  id: string
  workflow: CustomButtonWorkflow

  public constructor({metadata , type , name , workflow, id }) {
    this.metadata = metadata
    this.type = type
    this.name = name
    this.id = id
    this.workflow = workflow
  }
  set_metadata(key: string, val: any){
    if(!this.metadata){
      this.metadata = {}
    }
    this.metadata[key] = val
  }

  public async execute() {}

}
