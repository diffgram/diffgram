import {size, isEqual} from "lodash";
import {MousePosition, Point} from "../../types/mouse_position";
import {Instance} from "./instances/Instance";
import * as math from 'mathjs'
import InstanceStore from "../../helpers/InstanceStore";
import {File} from "../../types/files";
import {ImageAnnotationUIContext} from "../../types/AnnotationUIContext";

export class CanvasMouseTools {
  public mouse_position: MousePosition;
  public canvas_translate: any;
  public transform_matrix: any;
  public transform_matrix_inv: any;
  public canvas_rectangle: DOMRect;
  public canvas_ctx: CanvasRenderingContext2D;
  public canvas_elm: HTMLCanvasElement;
  public scale: number;
  public canvas_scale_global: number;
  public top_left_transformed: Point;
  public bottom_right_transformed: Point;
  public top_right_transformed: Point;
  public bottom_left_transformed: Point;
  public top_left: Point;
  public bottom_right: Point;
  public top_right: Point;
  public bottom_left: Point;

  public canvas_width: number;
  public canvas_height: number;

  public mouse_is_down: boolean


  constructor(
      mouse_position,
      canvas_translate,
      canvas_elm: HTMLCanvasElement,
      canvas_scale_global: number,
      canvas_width: number,
      canvas_height: number) {

    this.mouse_position = mouse_position;
    this.canvas_translate = canvas_translate;
    this.canvas_elm = canvas_elm;
    this.canvas_ctx = this.canvas_elm.getContext('2d')
    this.scale = 1;
    this.canvas_scale_global = canvas_scale_global;
    this.canvas_width = canvas_width
    this.canvas_height = canvas_height
  }
  public set_canvas_width_height(w, h){
    this.canvas_width = w
    this.canvas_height = h
  }
  public zoom_to_point(point, scale) {
    if (scale <= this.canvas_scale_global) {
      this.reset_transform_with_global_scale();
      this.scale = this.canvas_scale_global;
      return
    }
    this.reset_transform_with_global_scale();
    this.scale = this.canvas_scale_global;
    this.canvas_ctx.translate(point.x, point.y);
    this.canvas_ctx.scale(scale, scale)
    this.canvas_ctx.translate(-point.x, -point.y);
    this.scale *= scale;
  }

  public get_new_bounds_from_translate_x(movement_x, canvas_width, canvas_height) {
    this.canvas_ctx.save();
    this.canvas_ctx.translate(-movement_x, 0);
    var transform = this.canvas_ctx.getTransform();
    let min_point = this.map_point_from_matrix(1, 1, transform)
    let max_point = this.map_point_from_matrix(canvas_width, canvas_height, transform)
    this.canvas_ctx.restore();
    return {x_min: min_point.x, x_max: max_point.x, y_min: min_point.y, y_max: max_point.y}
  }

  public get_bounds() {
    var transform = this.canvas_ctx.getTransform();
    let min_point = this.map_point_from_matrix(1, 1, transform)
    let max_point = this.map_point_from_matrix(this.canvas_width - 1, this.canvas_height - 1, transform)
    return {min_point: min_point, max_point: max_point}
  }

  public get_new_bounds_from_translate_y(movement_y, canvas_width, canvas_height) {
    this.canvas_ctx.save();
    this.canvas_ctx.translate(0, -movement_y);
    var transform = this.canvas_ctx.getTransform();
    let min_point = this.map_point_from_matrix(1, 1, transform)
    let max_point = this.map_point_from_matrix(canvas_width, canvas_height, transform)
    this.canvas_ctx.restore();
    return {x_min: min_point.x, x_max: max_point.x, y_min: min_point.y, y_max: max_point.y}
  }

  public pan_x(movement_x) {
    this.canvas_ctx.translate(-movement_x, 0);
  }

  public pan_y(movement_y) {
    this.canvas_ctx.translate(0, -movement_y);
  }

  public getMousePos(canvas, evt) {
    var rect = canvas.getBoundingClientRect(), // abs. size of element
      scaleX = canvas.width / rect.width,    // relationship bitmap vs. element for x
      scaleY = canvas.height / rect.height;  // relationship bitmap vs. element for y

    return {
      x: (evt.clientX - rect.left) * scaleX,   // scale mouse coordinates after they have
      y: (evt.clientY - rect.top) * scaleY     // been adjusted to be relative to element
    }
  }

  public mouse_transform(event, mouse_position, canvas_element): void {

    if (canvas_element) {
      this.canvas_rectangle = canvas_element.getBoundingClientRect()
    }
    if (!this.canvas_rectangle) {
      return
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
    if (!canvas_width) {
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

  public map_point_from_matrix(x, y, matrix = this.canvas_ctx.getTransform()) {
    let point = {'x': undefined, 'y': undefined}
    point.x = x * matrix.a + y * matrix.c + matrix.e;
    point.y = x * matrix.b + y * matrix.d + matrix.f;
    return point
  }

  public get_translation(transform) {
    return {x: transform.e, y: transform.f}
  }

  public reset_transform_with_global_scale() {
    this.canvas_ctx.resetTransform();
    this.canvas_ctx.scale(this.canvas_scale_global, this.canvas_scale_global);
  }
  public isTransformReset() {
    const context = this.canvas_ctx
    let matrix = context.getTransform();

    // Check if the matrix is an identity matrix
    return matrix.a === 1 && matrix.b === 0 && matrix.c === 0 && matrix.d === 1 && matrix.e === 0 && matrix.f === 0;
  }

  public doesBboxCollide(
    x_min_transformed,
    x_max_transformed,
    y_min_transformed,
    y_max_transformed) {
    // The canvas width and height define the bounds
    let canvasMinX = 0;
    let canvasMaxX = this.canvas_width;
    let canvasMinY = 0;
    let canvasMaxY = this.canvas_height;

    // Check if there's an overlap along the x and y axes
    let xOverlap = (x_min_transformed <= canvasMaxX && x_max_transformed >= canvasMinX);
    let yOverlap = (y_min_transformed <= canvasMaxY && y_max_transformed >= canvasMinY);

    // If there's an overlap along both axes, the bounding box collides with the canvas
    return xOverlap && yOverlap;
  }


  public check_is_instance_in_viewport(
      instance: Instance) {

    let transform = this.canvas_ctx.getTransform()
    // Show all instances if no transforms apply (ie no zoom)
    if(this.isTransformReset()){
      return true
    }

    if(instance.soft_delete || instance.type === 'global'){
      return undefined
    }
    let min_transformed = this.map_point_from_matrix(instance.x_min, instance.y_min, transform);
    let max_transformed = this.map_point_from_matrix(instance.x_max, instance.y_max, transform);
    let isBboxInside = this.doesBboxCollide(min_transformed.x, max_transformed.x, min_transformed.y, max_transformed.y)
    if(isBboxInside){
      return true
    }
  }

  public perform_zoom_delta(zoom, point) {

    this.scale = this.scale * zoom;
    if (this.scale <= this.canvas_scale_global) {
      this.reset_transform_with_global_scale();
      this.scale = this.canvas_scale_global;
      return

    }
    if (this.scale >= 30) {
      this.scale = 30
    }
    let transform = this.canvas_ctx.getTransform();
    this.canvas_ctx.resetTransform();

    this.canvas_ctx.clearRect(
      0,
      0,
      this.canvas_elm.width,
      this.canvas_elm.height
    );

    this.canvas_ctx.translate(point.x, point.y);

    this.canvas_ctx.scale(zoom, zoom);

    this.canvas_ctx.translate(-point.x, -point.y);

    this.canvas_ctx.transform(transform.a, transform.b, transform.c, transform.d, transform.e, transform.f)
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

    let bounds_before_zoom

    let zoom_in = true;
    if (zoom < 1) {
      zoom_in = false
    }
    if (zoom_in) {
    } else {
      bounds_before_zoom = this.get_bounds()
    }

    this.perform_zoom_delta(zoom, point)

    // Auto Align Border Feature

    if (zoom_in == false) {
      this.auto_align_borders_on_zoom_out(bounds_before_zoom)
    }
  }

  public zoom_in() {
    let zoomIntensity = 0.1;
    let virtual_wheel = .4
    let center_point = {x: this.canvas_width / 2, y: this.canvas_height / 2}
    let zoom = Math.exp(virtual_wheel * zoomIntensity);
    this.perform_zoom_delta(zoom, center_point)
  }

  public zoom_out() {
    let point
    let bounds_before_zoom
    let zoomIntensity = 0.1;
    let virtual_wheel = -.4
    let zoom = Math.exp(virtual_wheel * zoomIntensity);
    bounds_before_zoom = this.get_bounds()
    this.perform_zoom_delta(zoom, point)
    this.auto_align_borders_on_zoom_out(bounds_before_zoom)
  }

  private auto_align_borders_on_zoom_out(bounds_before_zoom) {
    // https://diffgram.readme.io/docs/auto_align_borders_on_zoom_out

    let bounds_after_zoom = this.get_bounds()

    if (bounds_before_zoom != undefined) {

      // Check we are near border.
      // This helps this only fire when near border, and also helps avoid
      // large movements when heavily zoomed in, since naturally when zoomed in this value will be large.

      if (Math.abs(bounds_before_zoom.min_point.x) < 50) {
        // Move the new border based on new boundry after zooming
        // This number must always be positive, handling the case of the boundry crossing the mouse
        this.pan_x(Math.abs(bounds_after_zoom.min_point.x))
      }

      if (Math.abs(bounds_before_zoom.min_point.y) < 50) {
        this.pan_y(Math.abs(bounds_after_zoom.min_point.y))
      }

      // careful, we use global scale for this comparison not the combined scale
      let canvas_width_scaled = this.canvas_width * this.canvas_scale_global

      let distance_from_outer_edge_x = Math.abs(
        bounds_before_zoom.max_point.x - canvas_width_scaled)

      if (distance_from_outer_edge_x < 50) {
        this.pan_x(-Math.abs(
          bounds_after_zoom.max_point.x - canvas_width_scaled))
      }

      let canvas_height_scaled = this.canvas_height * this.canvas_scale_global

      let distance_from_outer_edge_y = Math.abs(
        bounds_before_zoom.max_point.y - canvas_height_scaled)

      if (distance_from_outer_edge_y < 50) {
        this.pan_y(-Math.abs(
          bounds_after_zoom.max_point.y - canvas_height_scaled))
      }
    }
  }

  private raw_point(event) {
    var rect = event.target.getBoundingClientRect();
    var x = event.clientX - rect.left; //x position within the element.
    var y = event.clientY - rect.top;  //y position within the element.
    // let x_raw = (event.clientX - this.canvas_rectangle.left)
    // let y_raw = (event.clientY - this.canvas_rectangle.top)
    let point = {'x': x, 'y': y}
    return point
  }
}
