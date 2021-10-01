export class CanvasMouseTools {
  private mouse_position: any;
  private canvas_translate: any;
  private canvas_rectangle: any;

  constructor(mouse_position, canvas_translate) {
    this.mouse_position = mouse_position;
    this.canvas_translate = canvas_translate;
  }

  public zoom_in(canvas_transform): number {
    canvas_transform.canvas_scale_local += 0.1;
    if (canvas_transform.canvas_scale_local >= 30) {
      canvas_transform.canvas_scale_local = 30
    }
    return canvas_transform.canvas_scale_local
  }

  public zoom_out(canvas_transform): number {
    canvas_transform.canvas_scale_local -= 0.1
    if (canvas_transform.canvas_scale_local < 1) {
      canvas_transform.canvas_scale_local = 1
    }
    return canvas_transform.canvas_scale_local
  }

  public clamp_values(val, min, max) {
    //https://stackoverflow.com/questions/11409895/whats-the-most-elegant-way-to-cap-a-number-to-a-segment
    return Math.min(Math.max(val, min), max)
  }

  public mouse_transform(event, mouse_position, canvas_element, update_canvas, canvas_transform): void {

    if (canvas_element) {
      this.canvas_rectangle = canvas_element.getBoundingClientRect()
    }
    // sometimes the canvas just doesn't seem to want to update correctly
    // if the left value is 0 there is most likely a problem so try to refresh teh canvas
    if (this.canvas_rectangle.left == 0) {
      // TODO: Discuss if we can remove this, I feel this is a bit hacky.
      update_canvas()
      this.canvas_rectangle = canvas_element.getBoundingClientRect()
    }

    let x_raw = (event.clientX - this.canvas_rectangle.left)
    let y_raw = (event.clientY - this.canvas_rectangle.top)

    let x = (((x_raw - this.canvas_translate.x) / canvas_transform.canvas_scale_local) + this.canvas_translate.x) / canvas_transform.canvas_scale_global
    let y = (((y_raw - this.canvas_translate.y) / canvas_transform.canvas_scale_local) + this.canvas_translate.y) / canvas_transform.canvas_scale_global

    // Note that we don't create a new object on purpose. We do this because we want to keep the reference on all the
    // class intances that are on this.instance_list(). You can see the initialize_instance() function to see
    // how the reference is passed.
    mouse_position.x = x;
    mouse_position.y = y;
    mouse_position.raw.x = x_raw;
    mouse_position.raw.y = y_raw;
    return mouse_position;
  }

  public zoom_wheel_scroll_canvas_transform_update(event, canvas_scale_local): number {
    event.preventDefault();
    canvas_scale_local += (.1 * event.wheelDelta / 100)

    if (canvas_scale_local < 1) {
      canvas_scale_local = 1
    }

    // TODO abstract this
    if (canvas_scale_local >= 30) {
      canvas_scale_local = 30
    }
    return canvas_scale_local
  }

  public zoom_wheel_canvas_translate(event, canvas_scale_local): number {

    // TODO: I would like to be smoother. In case of being zoomed in and then moving mouse, then zooming out it jerks
    // TODO if it's zoomed would like to get delta or cap this so it doesn't
    // "jerk" as much
    if (event.wheelDelta > 0) {
      let deltaX = this.mouse_position.raw.x - this.canvas_translate.x
      let deltaY = this.mouse_position.raw.y - this.canvas_translate.y
      // want clamp to decrease as scale is zoomed in?
      // ie so 100 / 5 = 20
      if (canvas_scale_local > 1.5) {
        // if statement is because for very intial most thing person could want
        // furtherest corner and there isn't a strong need to scale it.
        deltaX = this.clamp_values(deltaX,
          -80 / canvas_scale_local, 80 / canvas_scale_local)

        deltaY = this.clamp_values(deltaY,
          -80 / canvas_scale_local, 80 / canvas_scale_local)
      }

      this.canvas_translate.x += deltaX
      this.canvas_translate.y += deltaY
    }

    return this.canvas_translate
  }
}
