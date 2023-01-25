export default class HotKeyManager {
  annotation_type: String
  context: String
  key_down_handler: (this: Window, ev: KeyboardEvent) => void

  deactivate(): void {
    window.removeEventListener("keydown", this.key_down_handler)
  }

  activate(key_down_handler: (this: Window, ev: KeyboardEvent) => void): void {
    this.deactivate()
    
    this.key_down_handler = key_down_handler
    window.addEventListener("keydown", this.key_down_handler)
  }
}