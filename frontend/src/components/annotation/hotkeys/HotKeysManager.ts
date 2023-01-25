export default class HotKeyManager {
  annotation_type: String
  context: String
  key_down_handler: (this: Window, ev: KeyboardEvent) => void

  constructor(key_down_handler: (this: Window, ev: KeyboardEvent) => void) {
    this.key_down_handler = key_down_handler
  }

  deactivate(): void {
    window.removeEventListener("keydown", this.key_down_handler)
  }

  activate(): void {
    this.deactivate()
    window.addEventListener("keydown", this.key_down_handler)
  }
}