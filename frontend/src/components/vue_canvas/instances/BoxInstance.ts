import {InstanceBehaviour2D, Instance} from './Instance'
import {InstanceContext} from './InstanceContext';
import {v4 as uuidv4} from 'uuid';
import {getContrastColor} from '../../../utils/colorUtils'
import {MousePosition, point_is_intersecting_circle} from "../../../types/mouse_position";
import {get_sequence_color} from '../../regular/regular_annotation'
import {InstanceColor} from "../../../types/instance_color";
import {LabelColourMap} from "../../../types/label_colour_map";
import {ImageCanvasTransform} from "../../../types/CanvasTransform";

type BoxHoverPoints = 'x_min_y_min' | 'x_max_y_min' | 'x_min_y_max' | 'x_max_y_max' | 'not_intersecting_special_points' | 'blocked'

export class BoxInstance extends Instance implements InstanceBehaviour2D {
  public mouse_position: MousePosition;
  public ctx: CanvasRenderingContext2D;
  public canvas_element: HTMLCanvasElement;
  public canvas_transform: ImageCanvasTransform;
  public colour: InstanceColor;
  private vertex_size: number = 5;
  private line_width: number = 2;
  private strokeColor: string = 'black';
  private fillColor: string = 'white';
  public is_dragging_instance: boolean = false;
  public is_hovered: boolean = false;
  private is_actively_drawing: boolean = false;
  public is_moving: boolean = false;
  public mouse_down_delta_event: any = undefined;
  public mouse_down_position: any = undefined;
  public initialized: boolean = false;
  private box_edit_point_hover: BoxHoverPoints = undefined
  private nearest_points_dict: any = undefined
  private zoom_value: number = 1
  private font_size: number = 10


  public get_instance_data(): object {
    const result = super.get_instance_data();
    return result;
  }

  constructor(mouse_position: MousePosition = undefined,
              ctx: CanvasRenderingContext2D = undefined,
              on_instance_updated: Function = undefined,
              on_instance_selected: Function = undefined,
              on_instance_deselected: Function = undefined,
              mouse_down_delta_event = undefined,
              mouse_down_position = undefined,
              canvas_transform = undefined) {

    super();
    this.on_instance_updated = on_instance_updated;
    this.on_instance_selected = on_instance_selected;
    this.on_instance_deselected = on_instance_deselected;
    this.mouse_down_delta_event = mouse_down_delta_event;
    this.mouse_down_position = mouse_down_position;
    this.canvas_transform = canvas_transform;
    this.type = 'box'
    this.mouse_position = mouse_position;
    this.initialized = true;
    this.ctx = ctx;
  }
  public set_canvas(val: HTMLCanvasElement){
    this.canvas_element = val
    if(this.canvas_element){
      this.ctx = this.canvas_element.getContext("2d");
    }
  }

  public set_canvas_transform(val: ImageCanvasTransform) {
    this.canvas_transform = val
  }

  public get_canvas_transform(): ImageCanvasTransform {
    return this.canvas_transform
  }

  public set_actively_drawing(val: boolean): void {
    this.is_actively_drawing = val
  }

  public get_is_actively_drawing(): boolean {
    return this.is_actively_drawing;
  }

  private draw_currently_drawing_box(ctx: CanvasRenderingContext2D) {

    ctx.fillStyle = get_sequence_color(this.sequence_id)
    ctx.fillText(this.label_file.label.name, this.x_min, this.y_min);
    this.set_stroke_and_fill_styles(ctx, 1)
    ctx.setLineDash([0])
    ctx.rect(this.x_min,
      this.y_min,
      this.width,
      this.height)

    ctx.stroke()
  }

  private draw_finished_box() {

  }

  private set_stroke_and_fill_styles(ctx: CanvasRenderingContext2D, opacity: number) {
    let label_color_map = this.get_label_file_colour_map()
    this.colour = label_color_map[this.label_file.id]
    if (this.colour != undefined) {
      ctx.strokeStyle = this.colour.hex
      let r = this.colour.rgba.r
      let g = this.colour.rgba.g
      let b = this.colour.rgba.b
      ctx.fillStyle = "rgba(" + r + "," + g + "," + b + "," + opacity + ")";
    }
  }

  public set_mouse_cursor_from_hovered_point(movement_point: BoxHoverPoints){
    let movement_point_hover_style_map = {
      'x_min_y_min': 'nwse-resize',
      'x_max_y_min': 'nesw-resize',
      'x_min_y_max': 'nesw-resize',
      'x_max_y_max': 'nwse-resize',
      'not_intersecting_special_points': 'pointer',
      'blocked': 'not-allowed',

    }
    this.canvas_element.style.cursor = movement_point_hover_style_map[movement_point]
  }
  public determine_movement_point_for_box(): BoxHoverPoints {
    // if (this.lock_point_hover_change == true) {
    //   return false;
    // }


    let point_list = [
      [this.x_min, this.y_min, "x_min_y_min", "nwse-resize"],
      [this.x_max, this.y_min, "x_max_y_min", "nesw-resize"],
      [this.x_min, this.y_max, "x_min_y_max", "nesw-resize"],
      [this.x_max, this.y_max, "x_max_y_max", "nwse-resize"],
    ];

    for (let point of point_list) {
      let intersection = point_is_intersecting_circle(
        this.mouse_position,
        {
          x: point[0] as number,
          y: point[1] as number
        }
      );

      if (intersection == true) {
        this.box_edit_point_hover = point[2] as BoxHoverPoints;
        return this.box_edit_point_hover;
      }
    }
    this.box_edit_point_hover = "not_intersecting_special_points";

    this.set_mouse_cursor_from_hovered_point(this.box_edit_point_hover as BoxHoverPoints)

    return this.box_edit_point_hover;
  }
  public drag(mouse_delta: MousePosition){
    this.x_min += mouse_delta.x;
    this.y_min += mouse_delta.y;

    this.x_max += mouse_delta.x;
    this.y_max += mouse_delta.y;
    this.interpolated = false;
  }
  private invert_origin_on_overflow(){
    if (this.x_max < this.x_min) {
      let x_max_temp = this.x_max;
      this.x_max = this.x_min;
      this.x_min = x_max_temp;
    }

    if (this.y_max < this.y_min) {
      let y_max_temp = this.y_max;
      this.y_max = this.y_min;
      this.y_min = y_max_temp;
    }
  }
  private update_width_and_height(){
    this.width = this.x_max - this.x_min;
    this.height = this.y_max - this.y_min;

    this.status = "updated";

    // this.instance_list.splice(i, 1, instance);
  }
  public resize_from_mouse_position(event: MouseEvent, mouse_position: MousePosition) {

    let x_new = mouse_position.x;
    let y_new = mouse_position.y;

    let x_movement = parseInt(String(event.movementX / this.canvas_transform.canvas_scale_combined));
    let y_movement = Math.ceil(event.movementY / this.canvas_transform.canvas_scale_combined);



    if (this.box_edit_point_hover == "x_min_y_min") {
      this.x_min = x_new;
      this.y_min = y_new;
    } else if (this.box_edit_point_hover == "x_max_y_max") {
      this.x_max = x_new;
      this.y_max = y_new;
    } else if (this.box_edit_point_hover == "x_min_y_max") {
      this.x_min = x_new;
      this.y_max = y_new;
    } else if (this.box_edit_point_hover == "x_max_y_min") {
      this.x_max = x_new;
      this.y_min = y_new;
    }
    this.interpolated = false;
    this.invert_origin_on_overflow()
    this.update_width_and_height()
    // move whole box
    // else if (this.box_edit_point_hover == "not_intersecting_special_points") {
    //   this.drag(this.mouse_down_delta_event)
    //
    // }
  }
  public set_line_width(val: number){
    this.line_width = val
  }
  public draw(ctx: CanvasRenderingContext2D): void {
    ctx.beginPath()
    if (this.is_actively_drawing) {
      this.draw_currently_drawing_box(ctx)

    } else {
      this.draw_finished_box()
    }
    ctx.lineWidth = this.line_width
    ctx.stroke()
  }


}
