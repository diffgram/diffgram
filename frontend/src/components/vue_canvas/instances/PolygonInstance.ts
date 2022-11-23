import {InstanceBehaviour2D, Instance} from './Instance'
import {InstanceContext} from './InstanceContext';
import {v4 as uuidv4} from 'uuid';
import {getContrastColor} from '../../../utils/colorUtils'
import {MousePosition, Point, point_is_intersecting_circle} from "../../../types/mouse_position";
import {get_sequence_color} from '../../regular/regular_annotation'
import {InstanceColor} from "../../../types/instance_color";
import {LabelColourMap} from "../../../types/label_colour_map";
import {ImageCanvasTransform} from "../../../types/CanvasTransform";
import {InstanceImage2D} from "./InstanceImage2D";
import {ImageLabelSettings} from "../../../types/image_label_settings";

type BoxHoverPoints =
  'x_min_y_min'
  | 'x_max_y_min'
  | 'x_min_y_max'
  | 'x_max_y_max'
  | 'not_intersecting_special_points'
  | 'blocked'

export class PolygonInstance extends InstanceImage2D implements InstanceBehaviour2D {
  public mouse_position: MousePosition;
  public ctx: CanvasRenderingContext2D;
  public canvas_mouse_tools: ImageCanvasTransform;
  public colour: InstanceColor;
  public is_dragging_instance: boolean = false;
  public draw_corners: boolean = false;
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
              canvas_transform = undefined,
              image_label_settings: ImageLabelSettings = undefined) {

    super();
    this.on_instance_updated = on_instance_updated;
    this.on_instance_selected = on_instance_selected;
    this.on_instance_deselected = on_instance_deselected;
    this.mouse_down_delta_event = mouse_down_delta_event;
    this.mouse_down_position = mouse_down_position;
    this.canvas_transform = canvas_transform;
    this.image_label_settings = image_label_settings;
    this.type = 'polygon'
    this.mouse_position = mouse_position;
    this.initialized = true;
    this.on_instance_hovered = this.set_default_hover_in_style
    this.on_instance_unhovered = this.set_default_hover_out_style
    this.ctx = ctx;
  }

  public duplicate_for_undo() {
    let duplicate_instance = new PolygonInstance(
      this.mouse_position,
      this.ctx,
      this.on_instance_updated,
      this.on_instance_selected,
      this.on_instance_deselected,
      this.mouse_down_delta_event,
      this.mouse_down_position,
      this.image_label_settings,
    );
    let instance_data_to_keep = {
      ...this,
    };
    duplicate_instance.populate_from_instance_obj(instance_data_to_keep);
    return duplicate_instance
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

  public drag(mouse_delta: MousePosition) {
    this.x_min += mouse_delta.x;
    this.y_min += mouse_delta.y;

    this.x_max += mouse_delta.x;
    this.y_max += mouse_delta.y;
    this.interpolated = false;

    this.x_min = Math.ceil(this.x_min)
    this.y_min = Math.ceil(this.y_min)
    this.x_max = Math.ceil(this.x_max)
    this.y_max = Math.ceil(this.y_max)
  }


  private update_width_and_height() {
    this.width = this.x_max - this.x_min;
    this.height = this.y_max - this.y_min;

    this.width = Math.ceil(this.width)
    this.height = Math.ceil(this.height)
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
  public add_point(point: Point){
    this.points.push(point)
  }

  public update_min_max_points() {
    const point_max_x = this.points.reduce((previous: Point, current: Point): Point => {
      return current.x > previous.x ? current : previous;
    }) as Point;
    const point_min_x = this.points.reduce((previous: Point, current: Point) => {
      return current.x < previous.x ? current : previous;
    }) as Point;

    const point_min_y = this.points.reduce((previous: Point, current: Point) => {
      return current.y < previous.y ? current : previous;
    }) as Point;

    const point_max_y = this.points.reduce((previous: Point, current: Point) => {
      return current.y < previous.y ? current : previous;
    }) as Point;
    this.x_max = point_max_x.x;
    this.x_min = point_min_x.x;
    this.y_min = point_min_y.y;
    this.y_min = point_max_y.y;
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
    this.x_min = Math.ceil(this.x_min)
    this.y_min = Math.ceil(this.y_min)
    this.x_max = Math.ceil(this.x_max)
    this.y_max = Math.ceil(this.y_max)
  }
  public move_from_mouse_position(mouse_down_delta_event: MousePosition){
    this.x_min += mouse_down_delta_event.x;
    this.y_min += mouse_down_delta_event.y;

    this.x_max += mouse_down_delta_event.x;
    this.y_max += mouse_down_delta_event.y;

    this.x_min = Math.ceil(this.x_min)
    this.y_min = Math.ceil(this.y_min)
    this.x_max = Math.ceil(this.x_max)
    this.y_max = Math.ceil(this.y_max)
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
    let hover_point = this.determine_movement_point_for_box()
    this.hide_box_corners()
    if(!box.selected){

      this.set_color_from_label()
    }

  }

  private draw_circle(x, y, ctx) {
    ctx.arc(x, y, this.image_label_settings.vertex_size, 0, 2 * Math.PI);
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
    const prev_hover_point = this.box_edit_point_hover
    let box_hover_point = this.determine_movement_point_for_box()
    if (this.is_mouse_in_path(ctx) || box_hover_point != prev_hover_point) {
      if(!this.is_hovered){
        this.on_instance_hovered(this)
        this.is_hovered = true
        this.set_mouse_cursor_from_hovered_point(this.box_edit_point_hover)
      }
      if(prev_hover_point != box_hover_point){
        this.on_instance_hovered(this)
        this.is_hovered = true
        this.set_mouse_cursor_from_hovered_point(this.box_edit_point_hover)
      }

    } else {
      if(this.is_hovered && box_hover_point == 'not_intersecting_special_points'){
        this.is_hovered = false
        if(this.on_instance_unhovered){
          this.on_instance_unhovered(this)
        }
        this.set_mouse_cursor_from_hovered_point(this.box_edit_point_hover)
      }



    }
  }
  private draw_polygon_figure(ctx, points, figure_id){
    if(this.selected){
      this.generate_polygon_mid_points(instance, ctx, i, points, figure_id)
      this.draw_polygon_midpoints(instance, ctx, i, figure_id)
    }
    ctx.beginPath();
    const instance_colour = this.colour;
    let r = instance_colour.rgba.r
    let g = instance_colour.rgba.g
    let b = instance_colour.rgba.b
    const preStrokeStyle = ctx.strokeStyle;
    ctx.strokeStyle = preStrokeStyle;
    if (points.length >= 1) {

      this.draw_label(ctx, points[0].x, points[0].y, this)
      ctx.fillStyle = "rgba(" + r + "," + g + "," + b + `,${this.$props.default_instance_opacity})`;
      ctx.moveTo(points[0].x, points[0].y)

    }

    if (points.length >= 2) {
      this.draw_polygon_lines(instance, ctx, points)
      ctx.lineTo(points[0].x, points[0].y)
    }

    this.is_mouse_in_path(ctx, i, instance, figure_id) // must be seperate from when circles are drawn

    let spatial_line_size = this.get_spatial_line_size()
    if (spatial_line_size != 0) {
      ctx.lineWidth = spatial_line_size
      ctx.stroke()
    }

    // We may want these selection values to be user definable
    // Context of wanting a lower value when selected is so the person can still see the raw image
    // AND the overall coverage is still visible. Especially relevant if spatial_line is 0.
    if (this.selected == true && this.image_label_settings.default_instance_opacity != 1) {
      ctx.fillStyle = "rgba(" + r + "," + g + "," + b + ", .1)";
    }

    if (this.is_hovered && this.image_label_settings.default_instance_opacity != 1) {
      ctx.fillStyle = "rgba(" + r + "," + g + "," + b + ",.1)";
    }

    if (instance.type == "polygon") {
      ctx.fill()
    }
    if (instance.type == "line") {
      ctx.lineWidth *= 2
    }
  }
  private draw_polygon_main_section(ctx){
    let figure_id_list = [];

    for (const point of this.points){
      if(!point.figure_id){
        continue
      }
      if(!figure_id_list.includes(point.figure_id)){
        figure_id_list.push(point.figure_id)
      }
    }
    if(figure_id_list.length === 0){
      let points = this.points;
      this.draw_polygon_figure(instance, ctx, i, points)
    }
    else{
      for(const figure_id of figure_id_list){
        let points = this.points.filter(p => p.figure_id === figure_id);
        this.draw_polygon_figure(instance, ctx, i, points, figure_id)
      }
    }



    return true
  }
  public draw(ctx: CanvasRenderingContext2D): void {
    ctx.beginPath()
    if (this.sequence_id) {
      ctx.fillStyle = get_sequence_color(this.sequence_id)
    }


    this.draw_label(ctx, this.x_min, this.y_min)
    this.grab_color_from_instance(ctx)


    // this.check_box_hovered(ctx)
    // if (this.draw_corners || this.selected) {
    //   this.draw_box_edit_corners(ctx)
    // }
    //
    // if(this.image_label_settings){
    //   ctx.lineWidth = this.image_label_settings.spatial_line_size
    // }

    ctx.stroke()
  }


}
