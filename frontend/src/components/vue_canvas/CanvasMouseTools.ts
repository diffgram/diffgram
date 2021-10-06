export class CanvasMouseTools {
  private mouse_position: any;
  private canvas_translate: any;
  private canvas_rectangle: any;
  private canvas_transform: any;
  private canvas_ctx: any;
  private canvas_elm: any;
  private image: any;
  private scale: number;
  private translate_acc: { x: number, y: number };
  private canvas_translate_previous: { x: number, y: number };
  private previous_point: { x: number, y: number };


  constructor(mouse_position, canvas_translate, canvas_transform, canvas_elm, image) {
    this.mouse_position = mouse_position;
    this.canvas_translate = canvas_translate;
    this.canvas_transform = canvas_transform;
    this.canvas_elm = canvas_elm;
    this.image = image;
    this.canvas_ctx = this.canvas_elm.getContext('2d')
    this.scale = 1
    this.translate_acc = {x: 0, y: 0}
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

    // let x = (((x_raw - (this.canvas_translate_previous.x)) / canvas_transform.canvas_scale_local) + (this.canvas_translate.x)) / canvas_transform.canvas_scale_global
    // let y = (((y_raw - (this.canvas_translate_previous.y)) / canvas_transform.canvas_scale_local) + (this.canvas_translate.y)) / canvas_transform.canvas_scale_global
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
  public zoom_wheel(event): void {
    // this is the illusionary point on UI that we wish to stay locked on
    let point = this.raw_point(event);
    const wheel = event.deltaY < 0 ? 1 : -1;

    // Compute zoom factor.
    let zoomIntensity = 0.2;
    let zoom = Math.exp(wheel * zoomIntensity);
    this.scale = this.scale * zoom;

    if (this.scale <= 1) {
      this.canvas_ctx.resetTransform();
      this.scale = 1;
      let transform_new = this.canvas_ctx.getTransform();
    }
    if (this.scale >= 30) {
      this.scale = 30
    }
    this.canvas_ctx.clearRect(
      0,
      0,
      this.canvas_elm.width / this.scale,
      this.canvas_elm.height / this.scale
    );

    let transform = this.canvas_ctx.getTransform();
    this.canvas_ctx.resetTransform();
    this.canvas_ctx.translate(point.x, point.y);
    this.canvas_ctx.scale(zoom, zoom);
    this.canvas_ctx.translate(-point.x, -point.y);
    this.canvas_ctx.transform(transform.a, transform.b, transform.c, transform.d, transform.e, transform.f)
    let transform_new = this.canvas_ctx.getTransform();
    console.log('a', transform_new.a, 'd', transform_new.d)
    console.log('e', transform_new.e, 'f', transform_new.f)
    console.log('e', transform_new.e, 'f', transform_new.f)


    // Avoid negative translates
    if(transform_new.a < 1 || transform.d < 1){
      this.canvas_ctx.resetTransform();
    }
    if(transform_new.e > 0 || transform.f > 0){
      this.canvas_ctx.resetTransform();
    }
  }
  private raw_point(event) {
    let x_raw = (event.clientX - this.canvas_rectangle.left)
    let y_raw = (event.clientY - this.canvas_rectangle.top)
    let point = {'x': x_raw, 'y': y_raw}
    return point
  }
}
