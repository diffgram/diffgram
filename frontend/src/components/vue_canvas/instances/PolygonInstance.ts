import {InstanceBehaviour2D, Instance} from './Instance'
import {MousePosition, Point, point_is_intersecting_circle} from "../../../types/mouse_position";
import {get_sequence_color} from '../../regular/regular_annotation'
import {InstanceColor} from "../../../types/instance_color";
import {InstanceImage2D} from "./InstanceImage2D";
import {ImageLabelSettings} from "../../../types/image_label_settings";

export class PolygonInstance extends InstanceImage2D implements InstanceBehaviour2D {
  public ctx: CanvasRenderingContext2D;

  public colour: InstanceColor;
  public is_dragging_instance: boolean = false;
  public show_active_drawing_mouse_point: boolean = true;
  public draw_corners: boolean = false;
  public midpoints_polygon: { [p: number]: PolygonPoint[] } | PolygonPoint[] = null;
  public mouse_down_delta_event: any = undefined;
  public polygon_point_hover_index: number = undefined;
  public hovered_figure_id: string = undefined;
  public mouse_down_position: any = undefined;
  public initialized: boolean = false;
  public midpoint_hover: number = undefined
  private nearest_points_dict: any = undefined
  private zoom_value: number = 1
  private circle_size: number = null
  private auto_border_polygon_p1: PolygonPoint = null
  private auto_border_polygon_p2: PolygonPoint = null

  constructor(ctx: CanvasRenderingContext2D = undefined,
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
    this.initialized = true;
    this.on_instance_hovered = this.set_default_hover_in_style
    this.on_instance_unhovered = this.set_default_hover_out_style
    this.ctx = ctx;
  }
  public get_polygon_figures(): string[]{
    let figure_list = [];
    for (const p of this.points) {
      if (!p.figure_id) {
        continue;
      }
      if (!figure_list.includes(p.figure_id)) {
        figure_list.push(p.figure_id);
      }
    }
    return figure_list;
  }
  private find_midpoint_index(midpoints_polygon){
    let midpoint_hover = undefined;
    let count = 0;

    for (const point of midpoints_polygon) {
      // TODO use user set param here
      let result = point_is_intersecting_circle(
        this.canvas_mouse_tools.mouse_position,
        point,
        this.image_label_settings.vertex_size * 4
      );

      if (result) {
        midpoint_hover = count;
        this.canvas_element.style.cursor = "all-scroll";
      }
      count += 1;
    }
    if (midpoint_hover != undefined) {
      this.midpoint_hover = midpoint_hover;
    } else {
      this.midpoint_hover = undefined;
    }
    return midpoint_hover;
  }
  public detect_hover_polygon_midpoints(){
    const instance = this;
    if (!instance.selected) {
      return;
    }
    if (!instance.midpoints_polygon) {
      return;
    }

    // Check for hover on any middle point
    let midpoints_polygon = instance.midpoints_polygon;
    if (!Array.isArray(midpoints_polygon)) {
      for (let figure_id of Object.keys(midpoints_polygon)) {
        let figure_midpoints = midpoints_polygon[figure_id];
        let midpoint_hovered_point = this.find_midpoint_index(
          figure_midpoints
        );
        if (midpoint_hovered_point != undefined) {
          break;
        }
      }
    } else {
      this.find_midpoint_index(midpoints_polygon);
    }
  }
  public move_polygon_points(x_move: number, y_move: number, figure_id: string = undefined){
    let points = this.points;
    if (this.hovered_figure_id) {
      points = this.points.filter(
        (p) => p.figure_id === this.hovered_figure_id
      );
    }
    for (const point of points) {
      point.x += x_move;
      point.y += y_move;
    }
  }
  public duplicate_for_undo() {
    let duplicate_instance = new PolygonInstance(
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

  private check_polygon_intersection_on_points(): boolean {

    for (let i = 0; i < this.points.length; i++) {
      let result = point_is_intersecting_circle(
        this.canvas_mouse_tools.mouse_position,
        this.points[i],
        this.image_label_settings.vertex_size,
        this.zoom_value
      );

      if (result == true) {
        this.polygon_point_hover_index = i;
        this.set_mouse_cursor_from_hovered_point()
        return true;
      }
    }
    this.set_mouse_cursor_from_hovered_point()
    this.polygon_point_hover_index = null

    return false;
  }

  public set_mouse_cursor_from_hovered_point() {

    if (this.canvas_element) {
      if (this.polygon_point_hover_index != undefined) {
        this.canvas_element.style.cursor = 'all-scroll'
      } else {
        this.canvas_element.style.cursor = 'pointer'
      }

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

  public add_point(point: PolygonPoint) {
    this.points.push({...point} as PolygonPoint)
  }

  public update_min_max_points() {
    const point_max_x = this.points.reduce((previous: PolygonPoint, current: PolygonPoint): PolygonPoint => {
      return current.x > previous.x ? current : previous;
    }) as PolygonPoint;
    const point_min_x = this.points.reduce((previous: PolygonPoint, current: PolygonPoint) => {
      return current.x < previous.x ? current : previous;
    }) as PolygonPoint;

    const point_min_y = this.points.reduce((previous: PolygonPoint, current: PolygonPoint) => {
      return current.y < previous.y ? current : previous;
    }) as PolygonPoint;

    const point_max_y = this.points.reduce((previous: PolygonPoint, current: PolygonPoint) => {
      return current.y < previous.y ? current : previous;
    }) as PolygonPoint;
    this.x_max = point_max_x.x;
    this.x_min = point_min_x.x;
    this.y_min = point_min_y.y;
    this.y_min = point_max_y.y;
  }


  public move_from_mouse_position(mouse_down_delta_event: MousePosition) {
    // TODO: Add polygon drag logic here
  }

  public set_default_hover_in_style(polygon: PolygonInstance) {

    this.set_mouse_cursor_from_hovered_point()
    this.show_polygon_vertices()
  }

  public set_default_hover_out_style(polygon: PolygonInstance) {
    if (this.canvas_element) {
      this.canvas_element.style.cursor = 'default'
    }
    this.hide_polygon_vertices()
    if (!polygon.selected) {
      this.set_color_from_label()
    }

  }

  private draw_circle(x, y, ctx) {
    ctx.arc(x, y, this.image_label_settings.vertex_size, 0, 2 * Math.PI);
    ctx.moveTo(x, y) // reset
  }

  public show_polygon_vertices() {
    this.draw_corners = true
  }

  public hide_polygon_vertices() {
    this.draw_corners = false
  }

  private generate_polygon_mid_points(points, figure_id = undefined) {
    const midpoints_polygon = []
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1];
      const current = points[i];
      midpoints_polygon.push({
        x: (prev.x + current.x) / 2,
        y: (prev.y + current.y) / 2,
        figure_id: figure_id
      })
    }
    midpoints_polygon.push({
      x: (points[0].x + points[points.length - 1].x) / 2,
      y: (points[0].y + points[points.length - 1].y) / 2
    })
    if (figure_id) {
      if (!this.midpoints_polygon) {
        this.midpoints_polygon = {
          [figure_id]: midpoints_polygon
        }
      } else {
        this.midpoints_polygon[figure_id] = midpoints_polygon
      }

    } else {
      this.midpoints_polygon = midpoints_polygon;
    }
  }


  private draw_polygon_midpoints(ctx, figure_id = undefined) {
    let midpoints_polygon = this.midpoints_polygon
    if (figure_id) {
      midpoints_polygon = this.midpoints_polygon[figure_id] as PolygonPoint[]
    }
    if (this.midpoint_hover == undefined) {
      return
    }
    // Only draw when hovered in
    const point = midpoints_polygon[this.midpoint_hover] as Point;
    if (point == undefined) {
      return
    }
    const radius = (this.image_label_settings.vertex_size) / this.zoom_value
    this.draw_single_path_circle(point.x, point.y, radius, ctx);

  }

  private draw_single_path_circle(x, y, radius, ctx, strokeStyle = '#bdbdbd', fillStyle = 'white', lineWidth = '2px') {
    ctx.beginPath();
    ctx.strokeStyle = strokeStyle;
    ctx.fillStyle = fillStyle;
    ctx.lineWidth = lineWidth;
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.fill()
    ctx.stroke()
  }

  public delete_point(p_index: number){
    this.points.splice(p_index, 1);
  }

  private check_poly_hovered(ctx, figure_id: string = undefined) {

    if (this.is_mouse_in_path(ctx)) {
      this.check_polygon_intersection_on_points()
      if (!this.is_hovered) {
        this.is_hovered = true
        this.hovered_figure_id = figure_id
        if(this.on_instance_hovered){
          this.on_instance_hovered(this)
        }
      }
    }else{
      this.check_polygon_intersection_on_points()
      if(this.is_hovered && this.polygon_point_hover_index == undefined
        && this.midpoint_hover == undefined
        && (!figure_id || this.hovered_figure_id === figure_id)){
        this.set_mouse_cursor_from_hovered_point()
        this.is_hovered = false
        this.hovered_figure_id = null
        if(this.on_instance_unhovered){
          this.on_instance_unhovered(this)
        }
      }
    }

  }

  private draw_polygon_lines(ctx, points) {
    for (var j = 0; j < points.length - 1; j++) {
      ctx.lineTo(points[j + 1].x, points[j + 1].y)
    }
  }

  private draw_polygon_figure(ctx, points, figure_id = undefined) {
    if (this.selected) {
      this.generate_polygon_mid_points(points, figure_id)
      this.draw_polygon_midpoints(ctx, figure_id)
    }
    ctx.beginPath();
    const preStrokeStyle = ctx.strokeStyle;
    ctx.strokeStyle = this.strokeColor;
    if (points.length >= 1) {
      ctx.fillStyle = this.fillColor
      ctx.moveTo(points[0].x, points[0].y)
    }

    if (points.length >= 2) {
      this.draw_polygon_lines(ctx, points)
      ctx.lineTo(points[0].x, points[0].y)
    }


    let spatial_line_size = this.get_spatial_line_size()
    if (spatial_line_size != 0) {
      ctx.lineWidth = spatial_line_size
      ctx.stroke()
    }

    ctx.fill()
  }

  private draw_polygon_main_section(ctx) {
    let figure_id_list = [];
    for (const point of this.points) {
      if (!point.figure_id) {
        continue
      }
      if (!figure_id_list.includes(point.figure_id)) {
        figure_id_list.push(point.figure_id)
      }
    }
    if (figure_id_list.length === 0) {
      ctx.beginPath()
      let points = this.points;
      this.draw_polygon_figure(ctx, points)
      this.check_poly_hovered(ctx)
    } else {
      for (const figure_id of figure_id_list) {
        ctx.beginPath()
        let points = this.points.filter(p => p.figure_id === figure_id);
        this.draw_polygon_figure(ctx, points, figure_id)
        this.check_poly_hovered(ctx, figure_id)
      }
    }


    return true
  }

  private draw_many_polygon_circles(ctx) {

    // note different stopping point from lines
    const fillStyle = ctx.fillStyle;
    const strokeStyle = ctx.strokeStyle

    for (var j = 0; j < this.points.length; j++) {
      ctx.beginPath();
      ctx.fillStyle = '#ffffff';
      ctx.strokeStyle = '#bdbdbd';
      if (this.points[j].hovered_while_drawing) {
        ctx.fillStyle = 'white';
        ctx.strokeStyle = 'white';
      }
      if (this.points[j].point_set_as_auto_border) {
        ctx.fillStyle = '#4caf50';
        ctx.strokeStyle = '#4caf50';
      }
      this.draw_circle_from_instance(ctx, this.points, j)
      ctx.fillStyle = fillStyle;
      ctx.strokeStyle = strokeStyle;
    }
    ctx.fillStyle = fillStyle;
    ctx.strokeStyle = strokeStyle;
  }

  private draw_circle_from_instance(ctx, points, index) {
    let x = points[index].x
    let y = points[index].y

    this.draw_circle(x, y, ctx)
    ctx.fill();
    ctx.stroke();

  }

  private draw_autoborder_control_points(ctx) {
    let spatial_line_size = this.get_spatial_line_size()
    if (this.auto_border_polygon_p1) {
      this.draw_single_path_circle(this.auto_border_polygon_p1.x,
        this.auto_border_polygon_p1.y,
        this.circle_size,
        ctx,
        '#4caf50',
        '#4caf50',
        `${spatial_line_size}px`);
    }

    if (this.auto_border_polygon_p2) {

      this.draw_single_path_circle(this.auto_border_polygon_p2.x,
        this.auto_border_polygon_p2.y,
        this.circle_size,
        ctx,
        '#4caf50',
        '#4caf50',
        `${spatial_line_size}px`)
    }

  }
  public select(){
    super.select()
    this.show_polygon_vertices()
  }
  public unselect() {
    super.unselect();
    this.hide_polygon_vertices()
  }

  private draw_polygon_control_points(ctx) {
    ctx.beginPath();
    let points = this.points
    if (this.draw_corners || this.is_actively_drawing) {
      if (points.length >= 1) {
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#bdbdbd';
        if (this.points[0].hovered_while_drawing) {
          ctx.fillStyle = 'white';
          ctx.strokeStyle = 'white';
        }
        if (this.points[0].point_set_as_auto_border) {
          ctx.fillStyle = '#4caf50';
          ctx.strokeStyle = '#4caf50';
        }
        this.draw_circle_from_instance(ctx, points, 0)
      }
      if (points.length >= 2) {
        this.draw_many_polygon_circles(ctx)
      }

    }
    this.draw_autoborder_control_points(ctx)
    ctx.stroke()
  }

  public draw_actively_drawing_polygon(ctx) {
    let points = this.points
    let circle_size = 4 / this.zoom_value

    // If there is at least 2 points, draw the rest
    if (points.length >= 1) {
      if (this.number != undefined) {
        ctx.fillText(this.number, points[0].x, points[0].y)
      }
      ctx.fillText(this.label_file.label.name, points[0].x, points[0].y)

      for (var i = 0; i < points.length - 1; i++) {
        ctx.arc(points[i].x, points[i].y, circle_size, 0, 2 * Math.PI);
        ctx.lineTo(points[i + 1].x, points[i + 1].y)
      }
      ctx.arc(points[points.length - 1].x,
        points[points.length - 1].y, circle_size, 0, 2 * Math.PI);
      ctx.moveTo(points[i].x, points[i].y)
    }
    if (points.length >= 1 && this.show_active_drawing_mouse_point) {
      ctx.lineTo(this.canvas_mouse_tools.mouse_position.x, this.canvas_mouse_tools.mouse_position.y)

    }
    ctx.closePath()
    ctx.stroke()
    ctx.fill()
  }

  public draw(ctx: CanvasRenderingContext2D): void {

    this.zoom_value = this.ctx.getTransform().a
    this.circle_size = 6 / this.zoom_value
    ctx.setLineDash([0])

    if (this.sequence_id) {
      ctx.fillStyle = get_sequence_color(this.sequence_id)
    }


    this.draw_label(ctx, this.x_min, this.y_min)
    this.grab_color_from_instance(ctx)
    if (this.is_actively_drawing) {
      ctx.beginPath()
      this.draw_actively_drawing_polygon(ctx)

    } else {
      this.draw_polygon_main_section(ctx)
      this.draw_polygon_control_points(ctx)
    }


    // if (this.draw_corners || this.selected) {
    //   this.draw_box_edit_corners(ctx)
    // }
    //
    // if(this.image_label_settings){
    //   ctx.lineWidth = this.image_label_settings.spatial_line_size
    // }
    ctx.stroke()

  }

  public get_instance_data(): any {
    let data = super.get_instance_data()
    return {
      ...data,
      auto_border_polygon_p1: this.auto_border_polygon_p1,
      auto_border_polygon_p2: this.auto_border_polygon_p2,
    }
  }


}

export interface PolygonPoint extends Point {
  hovered_while_drawing: boolean
  point_set_as_auto_border: boolean
  selected?: boolean
  figure_id?: string
}

