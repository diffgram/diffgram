import {CustomButtonWorkflow} from "./CustomButtonWorkflow";

export class Button {
  display_name: string
  name: string
  icon: string

  constructor(display_name, name, icon) {
    this.name = name
    this.display_name = display_name
    this.icon = icon
  }
}



export class CustomButton extends Button {
  workflow: CustomButtonWorkflow
  color: string

  constructor({display_name, name, icon, workflow, color}) {
    super(display_name, name, icon)
    this.workflow = workflow
    this.color = color
  }

}
