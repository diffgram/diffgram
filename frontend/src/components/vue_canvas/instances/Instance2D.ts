import {Instance} from "chalk";


class Instance2D extends Instance{
  private is_mouse_in_stroke(ctx) {
    if (!this.mouse_position || !this.mouse_position.raw) {
      return false
    }
    if (ctx.isPointInStroke(
      this.mouse_position.raw.x,
      this.mouse_position.raw.y)) {
      return true;
    }
    return false

  }

  private is_mouse_in_path(ctx) {
    if (!this.mouse_position || !this.mouse_position.raw) {
      return false
    }
    if (ctx.isPointInPath(
      this.mouse_position.raw.x,
      this.mouse_position.raw.y)) {
      return true;
    }
    return false

  }
}
