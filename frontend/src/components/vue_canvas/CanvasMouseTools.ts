export class CanvasMouseTools {
  private mouse_position: any;
  private canvas_translate: any;
  private canvas_rectangle: any;
  private canvas_transform: any;
  private canvas_ctx: any;
  private canvas_elm: any;
  private previous_transform: any;
  private image: any;
  private scale: number;
  private previous_zoom: number;
  private canvas_scale_global: number;
  private translate_acc: { x: number, y: number };
  private canvas_translate_previous: { x: number, y: number };
  private previous_point: { x: number, y: number };


  constructor(mouse_position, canvas_translate, canvas_elm, canvas_scale_global) {
    this.mouse_position = mouse_position;
    this.canvas_translate = canvas_translate;
    this.canvas_elm = canvas_elm;
    this.canvas_ctx = this.canvas_elm.getContext('2d')
    this.scale = canvas_scale_global;
    this.canvas_scale_global = canvas_scale_global;
    this.translate_acc = {x: 0, y: 0}
  }

  public zoom_to_point(point, scale){
    this.reset_transform_with_global_scale();
    this.canvas_ctx.translate(point.x, point.y);
    this.canvas_ctx.scale(scale, scale)
    this.canvas_ctx.translate(-point.x, -point.y);
    this.scale = scale;
  }
  public pan_x(movement_x){
    this.canvas_ctx.translate(-movement_x, 0);
  }

  public pan_y(movement_y){
    this.canvas_ctx.translate(0, -movement_y);
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
    let x = (offsetX * target.width) / target.clientWidth;
    let y = (offsetY * target.height) / target.clientHeight;
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
  public get_translation(transform){
    return {x: transform.e, y: transform.f}
  }
  public reset_transform_with_global_scale(){
    this.canvas_ctx.resetTransform();
    this.canvas_ctx.scale(this.canvas_scale_global, this.canvas_scale_global);
    this.scale = this.canvas_scale_global;
  }

  public zoom_wheel(event): void {
    // this is the illusionary point on UI that we wish to stay locked on
    let point = this.raw_point(event);
    this.mouse_transform(event, this.mouse_position, this.canvas_elm)
    const wheel = event.deltaY < 0 ? 1 : -1;

    let transform = this.canvas_ctx.getTransform();
    // Compute zoom factor.
    let zoomIntensity = 0.1;
    let zoom = Math.exp(wheel * zoomIntensity);

    console.log('SCALEEE', this.scale)
    console.log('this.canvas_scale_global', this.canvas_scale_global)
    let point_changed = this.previous_point && (this.previous_point.x !== point.x || this.previous_point.y !== point.y)
    if (this.scale < this.canvas_scale_global) {

      this.reset_transform_with_global_scale();
      this.scale = this.canvas_scale_global;
      return
    }
    this.scale = this.scale * zoom;
    if (this.scale >= 30) {
      this.scale = 30
    }
    this.canvas_ctx.clearRect(
      0,
      0,
      this.canvas_elm.width,
      this.canvas_elm.height
    );


    this.reset_transform_with_global_scale();
    this.canvas_ctx.translate(point.x, point.y);

    this.canvas_ctx.scale(zoom, zoom);
    this.canvas_ctx.translate(-point.x, -point.y);

    this.canvas_ctx.transform(transform.a, transform.b, transform.c, transform.d, transform.e, transform.f)
    let transform_new = this.canvas_ctx.getTransform();
    console.log('a', transform_new.a, 'd', transform_new.d)
    console.log('e', transform_new.e, 'f', transform_new.f)
    console.log('e', transform_new.e, 'f', transform_new.f)


    // Avoid positive values translates
    if(transform_new.a < 1 || transform.d < 1){
      this.reset_transform_with_global_scale();
    }
    if(transform_new.e > 0 || transform.f > 0){
      this.reset_transform_with_global_scale();
    }
    this.previous_zoom = zoom;
    this.previous_point = point;
    this.previous_transform = transform;

  }
  private raw_point(event) {
    let x_raw = (event.clientX - this.canvas_rectangle.left)
    let y_raw = (event.clientY - this.canvas_rectangle.top)
    let point = {'x': x_raw, 'y': y_raw}
    return point
  }
}
