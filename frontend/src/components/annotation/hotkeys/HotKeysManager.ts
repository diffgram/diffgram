export default class HotKeyManager {
  annotation_type: String
  context: String
  key_listeners_map: any

  deactivate(): void {
    if (this.key_listeners_map) {
      window.removeEventListener("keydown", this.key_listeners_map["keydown"])
      window.removeEventListener("keyup", this.key_listeners_map["keyup"])
      window.removeEventListener("mousedown", this.key_listeners_map["mousedown"])
      window.removeEventListener("beforeunload", this.key_listeners_map["beforeunload"])
      window.removeEventListener("resize", this.key_listeners_map["resize"])
    }
  }

  activate(key_listeners_map: any): void {
    this.deactivate()

    this.key_listeners_map = key_listeners_map
    window.addEventListener("keydown", key_listeners_map["keydown"])
    window.addEventListener("keyup", key_listeners_map["keyup"])
    window.addEventListener("mousedown", key_listeners_map["mousedown"])
    window.addEventListener("beforeunload", key_listeners_map["beforeunload"])
    window.addEventListener("resize", key_listeners_map["resize"])
  }
}