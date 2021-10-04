export class CanvasMouseTools {
  private mouse_position: any;
  private canvas_translate: any;
  private canvas_rectangle: any;
  private canvas_transform: any;
  private scale: number;


  constructor(mouse_position, canvas_translate, canvas_transform) {
    this.mouse_position = mouse_position;
    this.canvas_translate = canvas_translate;
    this.canvas_transform = canvas_transform;
    this.scale = 1
  }

  public set_mouse_position(mouse_position) {
    this.mouse_position = mouse_position;
  }

  public set_canvas_translate(canvas_translate) {
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
    this.canvas_element = canvas_element;
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

  public zoom_wheel_scroll_canvas_transform_update(event, canvas_scale_local): {scale:number, zoom:number} {
    event.preventDefault();

    const wheel = event.deltaY < 0 ? 1 : -1;

    // Compute zoom factor.
    let zoomIntensity = 0.1;
    let zoom = Math.exp(wheel * zoomIntensity);
    let scale = canvas_scale_local * zoom;

    if (scale <= 1) {
      zoom = 1;
      scale = 1;
    }
    if (scale >= 30) {
      scale = 30
    }
    return {
      scale: scale,
      zoom: zoom
    }

    // event.preventDefault();
    // canvas_scale_local += (.1 * event.wheelDelta / 100)
    //
    // if (canvas_scale_local <= 1) {
    //   canvas_scale_local = 1
    //   this.canvas_translate.x = 0
    //   this.canvas_translate.y = 0
    // }
    //
    // // TODO abstract this
    // if (canvas_scale_local >= 30) {
    //   canvas_scale_local = 30
    // }
    // return canvas_scale_local
  }

  public zoom_wheel_canvas_translate(event, prior_scale, new_scale, canvas_scale_global): number {

    console.log('----------------------------')
    console.log('prior_scale', prior_scale)
    console.log('new_scale', new_scale)
    console.log('canvas_scale_global', canvas_scale_global)
    console.log('canvas_translate[x,y]', this.canvas_translate.x,  this.canvas_translate.y)

    // this is the illusionary point on UI that we wish to stay locked on
    let point = this.raw_point(event)
    let scaled_point = this.divide_point(point, new_scale, canvas_scale_global);
    let new_point = this.divide_point(point, prior_scale, canvas_scale_global);
    console.log('scaled_point', scaled_point.x, scaled_point.y)
    console.log('old_point', new_point.x, new_point.y)
    new_point = this.subtract_point(scaled_point, new_point);
    this.canvas_translate = this.subtract_point(this.canvas_translate, new_point);

    console.log('canvas_translate_new', this.canvas_translate.x, this.canvas_translate.y)
    this.scale *= new_scale;

    return this.canvas_translate
  }

  private raw_point(event) {
    let x_raw = (event.clientX - this.canvas_rectangle.left)
    let y_raw = (event.clientY - this.canvas_rectangle.top)
    let point = {'x': x_raw, 'y': y_raw}
    return point
  }

  private divide_point(point, scale, global) {
    let new_point = {'x': undefined, 'y': undefined}
    new_point.x = Math.round(point.x / scale / global)
    new_point.y = Math.round(point.y / scale / global)
    return new_point
  }


  private scale_point(point, scale, global) {
    let new_point = {'x': undefined, 'y': undefined}
    new_point.x = Math.round(point.x * scale * global)
    new_point.y = Math.round(point.y * scale * global)
    return new_point
  }

  private subtract_point(point, second_point) {
    let new_point = {'x': undefined, 'y': undefined}
    new_point.x = point.x - second_point.x
    new_point.y = point.y - second_point.y
    return new_point
  }

  private add_point(point, second_point) {
    let new_point = {'x': undefined, 'y': undefined}
    new_point.x = point.x + second_point.x
    new_point.y = point.y + second_point.y
    return new_point
  }
}
