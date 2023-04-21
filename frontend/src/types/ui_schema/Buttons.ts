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
  action_metadata: Object
  action_type: string

  constructor(type: string, metadata: Object) {
    this.action_type = type
    this.action_metadata = metadata

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
