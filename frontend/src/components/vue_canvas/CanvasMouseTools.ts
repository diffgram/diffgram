export class CanvasMouseTools {
  private mouse_position: any;
  private canvas_translate: any;
  private canvas_rectangle: any;
  private canvas_transform: any;
  private canvas_ctx: any;
  private canvas_elm: any;
  private zoom_stack: {point: {x: number, y: number}}[];
  private previous_transform: any;
  private panned_distance: {x: number, y: number}
  private image: any;
  private scale: number;
  private previous_zoom: number;
  private canvas_scale_global: number;
  private translate_acc: { x: number, y: number };
  private previous_point: { x: number, y: number };


  constructor(mouse_position, canvas_translate, canvas_elm, canvas_scale_global) {
    this.mouse_position = mouse_position;
    this.canvas_translate = canvas_translate;
    this.canvas_elm = canvas_elm;
    this.canvas_ctx = this.canvas_elm.getContext('2d')
    this.scale = 1;
    this.canvas_scale_global = canvas_scale_global;
    this.translate_acc = {x: 0, y: 0}
    this.zoom_stack = [];
    this.panned_distance = {x: 0, y: 0}
  }

  public zoom_to_point(point, scale){
    this.reset_transform_with_global_scale();
    this.scale = this.canvas_scale_global;
    this.canvas_ctx.translate(point.x, point.y);
    this.canvas_ctx.scale(scale, scale)
    this.canvas_ctx.translate(-point.x, -point.y);
    this.scale *= scale;
  }
  public get_new_bounds_from_translate_x(movement_x, canvas_width, canvas_height){
    this.canvas_ctx.save();
    this.canvas_ctx.translate(-movement_x, 0);
    var transform = this.canvas_ctx.getTransform();
    let min_point = this.map_point_from_matrix(1, 1, transform)
    let max_point = this.map_point_from_matrix(canvas_width, canvas_height, transform)
    this.canvas_ctx.restore();
    return {x_min: min_point.x, x_max: max_point.x, y_min: min_point.y, y_max: max_point.y}
  }

  public get_new_bounds_from_translate_y(movement_y, canvas_width, canvas_height){
    this.canvas_ctx.save();
    this.canvas_ctx.translate(0, -movement_y);
    var transform = this.canvas_ctx.getTransform();
    let min_point = this.map_point_from_matrix(1, 1, transform)
    let max_point = this.map_point_from_matrix(canvas_width, canvas_height, transform)
    this.canvas_ctx.restore();
    return {x_min: min_point.x, x_max: max_point.x, y_min: min_point.y, y_max: max_point.y}
  }
  public pan_x(movement_x){
    this.canvas_ctx.translate(-movement_x, 0);
    this.panned_distance.x += movement_x

  }

  public pan_y(movement_y){
    this.canvas_ctx.translate(0, -movement_y);
    this.panned_distance.y += movement_y

  }

  public mouse_transform(event, mouse_position, canvas_element): void {
    if (canvas_element) {
      this.canvas_rectangle = canvas_element.getBoundingClientRect()
    }

    let x_raw = (event.clientX - this.canvas_rectangle.left)
    let y_raw = (event.clientY - this.canvas_rectangle.top)
    event = event || window.event;
    var target = event.target || event.srcElement,
      style = target.currentStyle || window.getComputedStyle(target, null),
      borderLeftWidth = parseInt(style["borderLeftWidth"], 10),
      borderTopWidth = parseInt(style["borderTopWidth"], 10),
      rect = target.getBoundingClientRect(),
      offsetX = event.clientX - borderLeftWidth - rect.left,
      offsetY = event.clientY - borderTopWidth - rect.top;
    let canvas_width = target.width;
    let canvas_height = target.height;
    if(!canvas_width){
      canvas_width = this.canvas_elm.width;
      canvas_height = this.canvas_elm.height;
    }
    let x = (offsetX * canvas_width) / target.clientWidth;
    let y = (offsetY * canvas_height) / target.clientHeight;

    const ctx = this.canvas_ctx;
    var transform = ctx.getTransform();
    const invMat = transform.invertSelf();

    x = x * invMat.a + y * invMat.c + invMat.e;
    y = x * invMat.b + y * invMat.d + invMat.f;
    // Note that we don't create a new object on purpose. We do this because we want to keep the reference on all the
    // class intances that are on this.instance_list(). You can see the initialize_instance() function to see
    // how the reference is passed.
    mouse_position.x = x;
    mouse_position.y = y;
    mouse_position.raw.x = x_raw;
    mouse_position.raw.y = y_raw;

    return mouse_position;
  }

  public map_point_from_matrix(x, y, matrix){
    let point = {'x': undefined, 'y': undefined}
    point.x = x * matrix.a + y * matrix.c + matrix.e;
    point.y = x * matrix.b + y * matrix.d + matrix.f;
    return point
  }

  public get_translation(transform){
    return {x: transform.e, y: transform.f}
  }
  public reset_transform_with_global_scale(){
    this.canvas_ctx.resetTransform();
    this.canvas_ctx.scale(this.canvas_scale_global, this.canvas_scale_global);
    this.zoom_stack = [];
    this.panned_distance = {x: 0, y: 0}
  }

  public perform_zoom_delta(zoom, point){
    let point_changed = this.previous_point && (this.previous_point.x !== point.x || this.previous_point.y !== point.y)
    // this.panned_distance = {x: 0, y: 0}
    this.scale = this.scale * zoom;
    if (this.scale <= this.canvas_scale_global) {
      this.reset_transform_with_global_scale();
      this.scale = this.canvas_scale_global;
      return

    }
    if (this.scale >= 30) {
      this.scale = 30
    }
    this.canvas_ctx.clearRect(
      0,
      0,
      this.canvas_elm.width,
      this.canvas_elm.height
    );
    let transform = this.canvas_ctx.getTransform();
    this.canvas_ctx.resetTransform();

    this.canvas_ctx.translate(point.x, point.y);

    this.canvas_ctx.scale(zoom, zoom);
    this.canvas_ctx.translate(-point.x, -point.y);

    this.canvas_ctx.transform(transform.a, transform.b, transform.c, transform.d, transform.e, transform.f)
    let transform_new = this.canvas_ctx.getTransform();

    this.previous_zoom = zoom;
    this.previous_point = point;
    this.previous_transform = transform;
  }

  public zoom_wheel(event): void {
    event.preventDefault()
    event.stopPropagation()

    const wheel = event.deltaY < 0 ? 1 : -1;
    // Compute zoom factor.
    let zoomIntensity = 0.1;
    let zoom = Math.exp(wheel * zoomIntensity);

    // this is the illusionary point on UI that we wish to stay locked on
    let point = this.raw_point(event);

    let zoom_in = true;
    if(zoom < 1){
      zoom_in = false
    }
    if(zoom_in){
      this.zoom_stack.push({
        point: point
      });
    }
    else{
      let elm = this.zoom_stack.pop()
      if(elm){
        point = elm.point
        let panned_distance = this.panned_distance
        // Unpan
        this.canvas_ctx.translate(panned_distance.x, panned_distance.y)
        this.panned_distance = {x: 0, y: 0};
        console.log('POINT', point.x, point.y)
        console.log('pann', panned_distance.x, panned_distance.y)
        point.x += panned_distance.x;
        point.y += panned_distance.y;
      }

    }

    this.perform_zoom_delta(zoom, point)






  }
  private raw_point(event) {
    let x_raw = (event.clientX - this.canvas_rectangle.left)
    let y_raw = (event.clientY - this.canvas_rectangle.top)
    let point = {'x': x_raw, 'y': y_raw}
    return point
  }
}
