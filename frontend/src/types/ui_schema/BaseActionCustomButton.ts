import {CustomButtonWorkflow} from "./CustomButtonWorkflow";


export abstract class BaseActionCustomButton {
  metadata: object
  type: string
  name: string
  workflow: CustomButtonWorkflow

  public constructor({metadata , type , name , workflow }) {
    this.metadata = metadata
    this.type = type
    this.name = name
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
