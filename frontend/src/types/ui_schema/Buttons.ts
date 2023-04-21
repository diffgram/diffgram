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

export class ActionCustomButton {
  metadata: Object
  type: string

  constructor(type: string, metadata: Object) {
    this.type = type
    this.metadata = metadata
  }

  public set_metadata(key: string, val: any){
    if(!this.metadata){
      this.metadata = {}
    }
    this.metadata[key] = val
  }

}

export class CustomButton extends Button {
  action: ActionCustomButton
  color: string

  constructor(display_name: string, name: string, icon: string, action: ActionCustomButton, color: string) {
    super(display_name, name, icon)
    this.action = action
    this.color = color
  }

}
