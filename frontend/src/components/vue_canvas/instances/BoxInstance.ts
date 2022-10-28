import {InstanceBehaviour2D, Instance} from './Instance'
import {InstanceContext} from './InstanceContext';
import {v4 as uuidv4} from 'uuid';
import {getContrastColor} from '../../../utils/colorUtils'
import {MousePosition, point_is_intersecting_circle} from "../../../types/mouse_position";
import {get_sequence_color} from '../../regular/regular_annotation'
import {InstanceColor} from "../../../types/instance_color";
import {LabelColourMap} from "../../../types/label_colour_map";
import {ImageCanvasTransform} from "../../../types/CanvasTransform";

type BoxHoverPoints =
  'x_min_y_min'
  | 'x_max_y_min'
  | 'x_min_y_max'
  | 'x_max_y_max'
  | 'not_intersecting_special_points'
  | 'blocked'

export class BoxInstance extends Instance implements InstanceBehaviour2D {
  public mouse_position: MousePosition;
  public ctx: CanvasRenderingContext2D;
  public canvas_mouse_tools: ImageCanvasTransform;
  public colour: InstanceColor;
  private vertex_size: number = 5;
  private line_width: number = 2;
  public is_dragging_instance: boolean = false;
  public draw_corners: boolean = false;
  private is_actively_drawing: boolean = false;
  public is_moving: boolean = false;
  public mouse_down_delta_event: any = undefined;
  public mouse_down_position: any = undefined;
  public initialized: boolean = false;
  public box_edit_point_hover: BoxHoverPoints = undefined
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
    this.on_instance_hovered = this.set_default_hover_in_style
    this.on_instance_unhovered = this.set_default_hover_out_style
    this.ctx = ctx;
  }

  public remove_listener(event_type: string, callback: Function) {
    if(event_type === 'hover_in'){
      this.on_instance_hovered = null
    }
    if(event_type === 'hover_out'){
      this.on_instance_unhovered = null
    }
  }
  public set_is_resizing(val: boolean){
    this.is_resizing = val
  }
  public set_is_moving(val: boolean){
    this.is_moving = val
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


  public set_mouse_cursor_from_hovered_point(movement_point: BoxHoverPoints) {
    let movement_point_hover_style_map = {
      'x_min_y_min': 'nwse-resize',
      'x_max_y_min': 'nesw-resize',
      'x_min_y_max': 'nesw-resize',
      'x_max_y_max': 'nwse-resize',
      'not_intersecting_special_points': 'pointer',
      'blocked': 'not-allowed',

    }
    if(this.canvas_element){
      this.canvas_element.style.cursor = movement_point_hover_style_map[movement_point]
    }

  }

  public determine_movement_point_for_box(): BoxHoverPoints {
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

    return this.box_edit_point_hover;
  }

  public drag(mouse_delta: MousePosition) {
    this.x_min += mouse_delta.x;
    this.y_min += mouse_delta.y;

    this.x_max += mouse_delta.x;
    this.y_max += mouse_delta.y;
    this.interpolated = false;
  }

  private invert_origin_on_overflow() {
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
    if (this.x_min < 0) {
      this.x_min = 0;
    }
    if (this.y_min < 0) {
      this.y_min = 0;
    }
  }

  private update_width_and_height() {
    this.width = this.x_max - this.x_min;
    this.height = this.y_max - this.y_min;

    this.status = "updated";
  }

  private check_canvas_overflow() {
    if (this.canvas_transform && this.canvas_transform.canvas_width) {
      if (this.x_max >= this.canvas_transform.canvas_width) {
        this.x_max = this.canvas_transform.canvas_width - 1;
      }

      if (this.y_max >= this.canvas_transform.canvas_height) {
        this.y_max = this.canvas_transform.canvas_height - 1;
      }
    }
  }

  public update_min_max_points() {
    // For boxes, no special calculations are needed for min max point calculation.
  }

  public resize_from_corner_drag(mouse_position: MousePosition) {
    let x_new = mouse_position.x;
    let y_new = mouse_position.y;
    let movement_point_hover = this.box_edit_point_hover
    if(!this.is_resizing){
      let movement_point_hover = this.determine_movement_point_for_box()
    }

    this.set_mouse_cursor_from_hovered_point(movement_point_hover)
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
    this.is_resizing = true
    this.invert_origin_on_overflow()
    this.update_width_and_height()
    this.update_min_max_points()
    this.check_canvas_overflow()
  }
  public move_from_mouse_position(mouse_down_delta_event: MousePosition){
    this.x_min += mouse_down_delta_event.x;
    this.y_min += mouse_down_delta_event.y;

    this.x_max += mouse_down_delta_event.x;
    this.y_max += mouse_down_delta_event.y;
  }
  public resize_from_mouse_position(event: MouseEvent, mouse_position: MousePosition, mouse_down_position: MousePosition) {
    this.x_min = Math.ceil(mouse_down_position.x);
    this.y_min = Math.ceil(mouse_down_position.y);
    this.x_max = Math.ceil(mouse_position.x);
    this.y_max = Math.ceil(mouse_position.y);
    this.interpolated = false;
    this.invert_origin_on_overflow()
    this.update_width_and_height()
    this.update_min_max_points()
    this.check_canvas_overflow()
    // move whole box
    // else if (this.box_edit_point_hover == "not_intersecting_special_points") {
    //   this.drag(this.mouse_down_delta_event)
    //
    // }
  }

  public set_default_hover_in_style(box: BoxInstance) {
    let hover_point = this.determine_movement_point_for_box()

    this.set_mouse_cursor_from_hovered_point(hover_point)
    this.show_box_corners()
  }

  public set_default_hover_out_style(box: BoxInstance) {
    if(this.canvas_element){
      this.canvas_element.style.cursor = 'default'
    }
    this.hide_box_corners()
    if(!box.selected){

      this.set_color_from_label()
    }

  }



  public set_line_width(val: number) {
    this.line_width = val
  }

  private draw_circle(x, y, ctx) {
    ctx.arc(x, y, this.vertex_size, 0, 2 * Math.PI);
    ctx.moveTo(x, y) // reset
  }

  public show_box_corners() {
    this.draw_corners = true
  }

  public hide_box_corners() {
    this.draw_corners = false
  }

  private draw_box_edit_corners(ctx) {
    this.draw_circle(this.x_min, this.y_min, ctx)
    ctx.moveTo(this.x_max, this.y_min);
    this.draw_circle(this.x_max, this.y_min, ctx)
    ctx.moveTo(this.x_max, this.y_max);
    this.draw_circle(this.x_max, this.y_max, ctx)
    ctx.moveTo(this.x_min, this.y_max);
    this.draw_circle(this.x_min, this.y_max, ctx)
    ctx.fill()
  }

  private check_box_hovered(ctx) {
    if (this.is_mouse_in_path(ctx)) {
      this.is_hovered = true
      this.on_instance_hovered(this)
    } else {
      this.is_hovered = false
      this.on_instance_unhovered(this)
    }
  }

  public draw(ctx: CanvasRenderingContext2D): void {
    ctx.beginPath()
    if (this.sequence_id) {
      ctx.fillStyle = get_sequence_color(this.sequence_id)
    }

    this.grab_color_from_instance(ctx)
    ctx.fillText(this.label_file.label.name, this.x_min, this.y_min);
    ctx.setLineDash([0])
    ctx.rect(this.x_min,
      this.y_min,
      this.width,
      this.height)

    this.check_box_hovered(ctx)
    if (this.draw_corners || this.selected) {
      this.draw_box_edit_corners(ctx)
    }
    ctx.lineWidth = this.line_width
    ctx.stroke()
  }


}
