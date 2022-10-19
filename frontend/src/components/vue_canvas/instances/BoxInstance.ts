import {InstanceBehaviour2D, Instance} from './Instance'
import {InstanceContext} from './InstanceContext';
import {v4 as uuidv4} from 'uuid';
import {getContrastColor} from '../../../utils/colorUtils'

export class BoxInstance extends Instance implements InstanceBehaviour2D {
  public mouse_position: MousePo;
  public ctx: CanvasRenderingContext2D;
  private vertex_size: number = 5;
  private line_width: number = 2;
  private strokeColor: string = 'black';
  private fillColor: string = 'white';
  public instance_context: InstanceContext = undefined;
  public is_dragging_instance: boolean = false;
  public is_hovered: boolean = false;
  public is_moving: boolean = false;
  public mouse_down_delta_event: any = undefined;
  public mouse_down_position: any = undefined;
  public initialized: boolean = false;
  public label_settings: any = undefined
  private nearest_points_dict: any = undefined
  private zoom_value: number = 1


  public get_instance_data(): object {
    const result = super.get_instance_data();
    return result;
  }

  constructor(mouse_position = undefined,
              ctx = undefined,
              instance_context = undefined,
              on_instance_updated = undefined,
              on_instance_selected = undefined,
              on_instance_deselected = undefined,
              mouse_down_delta_event = undefined,
              mouse_down_position = undefined,
              label_settings = undefined) {

    super();
    this.on_instance_updated = on_instance_updated;
    this.on_instance_selected = on_instance_selected;
    this.on_instance_deselected = on_instance_deselected;
    this.mouse_down_delta_event = mouse_down_delta_event;
    this.mouse_down_position = mouse_down_position;
    this.instance_context = instance_context;
    this.type = 'box'
    this.mouse_position = mouse_position;
    this.initialized = true;
    this.ctx = ctx;
    this.label_settings = label_settings;
    if (this.label_settings) {
      this.vertex_size = this.label_settings.vertex_size
      this.line_width = this.label_settings.spatial_line_size
    } else {
      this.label_settings = {}
      this.label_settings.vertex_size = this.vertex_size
      this.label_settings.line_width = this.line_width
      this.label_settings.font_size = 20
    }
  }



  public contextmenu(event): void {
  }

  public process_mouse_up(): boolean {

    return false
  }


  private get_angle_of_from_rotation_control_movement() {
    // Read: https://math.stackexchange.com/questions/361412/finding-the-angle-between-three-points
    let center = {x: this.center_x, y: this.center_y}

    let B = {x: center.x, y: center.y}
    let C = {x: this.mouse_position.x, y: this.mouse_position.y}
    // let C = {x: rotate_point.x, y: rotate_point.y}

    let BC = {x: C.x - B.x, y: C.y - B.y}
    // BC = this.get_rotated_point(B, this.angle)
    // let theta = Math.acos(BA_dot_BC / (BA_len * BC_len))
    let theta = -Math.atan2(BC.x, BC.y)
    let angle = 0;
    angle += theta
    return angle;
  }

  public stop_dragging() {
    this.is_dragging_instance = false;

  }

  public start_dragging() {
    this.is_dragging_instance = true;
  }




  private draw_instance_bounding_box(ctx) {
    if(this.template_creation_mode){
      return
    }
    let min_max_obj = this.get_rotated_min_max();
    let width = Math.abs(min_max_obj.max_x - min_max_obj.min_x);
    let height = Math.abs(min_max_obj.max_y - min_max_obj.min_y);
    ctx.globalAlpha = 0.4;
    ctx.lineWidth = this.label_settings.spatial_line_size / this.zoom_value
    ctx.beginPath();

    ctx.rect(min_max_obj.min_x, min_max_obj.min_y, width + this.vertex_size, height + this.vertex_size);
    if (this.selected) {
      ctx.stroke()
      ctx.fill()
    }
    if (this.is_mouse_in_path(ctx) && !this.instance_context.draw_mode && !this.other_instance_hovered()) {
      this.is_bounding_box_hovered = true;
      this.is_hovered = true;
      // Draw helper bounding box
      if (!this.selected) {
        ctx.fillStyle = 'white'
        ctx.globalAlpha = 0.2;
        ctx.stroke()
        ctx.fill()
      }
    } else {
      this.is_bounding_box_hovered = false;
    }
    ctx.globalAlpha = 1;
  }

  private get_square_delta_point_mouse(point, mouse): number {
    return Math.sqrt(
      (point.x - mouse.x) ** 2
      + (mouse.y - point.y) ** 2)
  }

  private point_is_intersecting_circle(point, mouse, radius): boolean {

    return Math.sqrt(
      (point.x - mouse.x) ** 2
      + (mouse.y - point.y) ** 2) < radius
  }

  private set_node_hovered(ctx, i): void {
    this.is_hovered = true;
    this.is_node_hovered = true;
    this.node_hover_index = i
    this.num_hovered_paths += 1
  }

  private draw_point_and_set_node_hover_index(node, x, y, i, ctx): void {
    ctx.beginPath();
    if (this.node_hover_index === i) {
      if(!this.instance_context.color_tool_active){
        if(node.color){
          let hovercolor = getContrastColor(node.color.hex);
          ctx.fillStyle = hovercolor
          ctx.strokeStyle = hovercolor
        }
        else{
          if(node.color){
            let hovercolor = getContrastColor(node.color.hex);
            ctx.strokeStyle = hovercolor
            ctx.fillStyle = hovercolor
          }
          else{
            ctx.strokeStyle = 'green'
            ctx.fillStyle = 'green'
          }

        }
      }


    }
    else{
      this.set_node_color(node, ctx)
    }
    ctx.lineWidth = 2 / this.zoom_value
    ctx.arc(x, y, this.vertex_size / this.zoom_value, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.fill();

    let point = {'x': x, 'y': y}
    this.nearest_points_dict[this.get_square_delta_point_mouse(
      point,
      this.mouse_position)] = i
  }

  private draw_currently_drawing_edge(ctx) {
    if (!this.is_drawing_edge) {
      return
    }
    if (!this.mouse_position) {
      return
    }
    if (this.current_node_connection.length === 0) {
      return
    }
    if (!this.current_node_connection[0]) {
      return
    }
    ctx.beginPath();
    ctx.lineWidth = this.label_settings.spatial_line_size / this.zoom_value;
    ctx.setLineDash([])
    ctx.moveTo(this.current_node_connection[0].x, this.current_node_connection[0].y);
    ctx.lineTo(this.mouse_position.x, this.mouse_position.y)
    ctx.stroke()
    ctx.fill();

  }

  public occlude_direction(end_index) {
    let start_node = this.nodes[this.start_index_occlusion]
    let end_node = this.nodes[end_index]
    let edge_from = this.edges.find(e => e.from === start_node.id && e.to === end_node.id);
    let edge_to = this.edges.find(e => e.to === start_node.id && e.from === end_node.id);

    let edge = edge_from;
    if (!edge) {
      edge = edge_to;
      if (!edge) {
        return
      }
    }
    start_node.occluded = true;
    let pending_nodes = [end_node]
    while (pending_nodes.length > 0) {
      let next_node = pending_nodes.shift();
      let adjacent = this.edges.filter(edge => edge.from === next_node.id || edge.to === next_node.id);
      for (let adj_edge of adjacent) {
        let node_from = this.nodes.find(n => n.id === adj_edge.from);
        let node_to = this.nodes.find(n => n.id === adj_edge.to);
        if (node_from && !node_from.occluded) {
          node_from.occluded = true;
          pending_nodes.push(node_from)
        }
        if (node_to && !node_to.occluded) {
          node_to.occluded = true;
          pending_nodes.push(node_to)
        }
      }
    }

  }

  public stop_occlude_direction() {
    this.start_index_occlusion = undefined;
  }

  public activate_select_edge_occlusion(node_index: number) {
    this.start_index_occlusion = node_index;
  }

  private draw_edges(ctx) {
    if(this.guided_mode_active){
      return
    }
    ctx.lineWidth = this.label_settings.spatial_line_size / this.zoom_value;
    if (this.template_creation_mode) {
      ctx.lineWidth = 6 / this.zoom_value
    }
    ctx.setLineDash([])
    this.is_edge_hovered = false;
    for (let edge of this.edges) {

      ctx.beginPath();
      ctx.strokeStyle = this.strokeColor

      let node1 = this.nodes.filter(n => n.id === edge.from)[0];
      let node2 = this.nodes.filter(n => n.id === edge.to)[0];

      if (this.label_settings &&
        this.label_settings.show_occluded_keypoints == false &&
        node2.occluded == true) {
        continue
      }


      if (edge.is_hovered) {
        ctx.strokeStyle = 'green'
      }
      if (edge.color) {
        ctx.strokeStyle = edge.color.hex;
      }
      if (node1 && node2) {
        if (node2.occluded == true || node1.occluded == true) {
          ctx.globalAlpha = 0.3;
        }
        let x1 = this.get_scaled_x(node1);
        let x2 = this.get_scaled_x(node2);
        let y1 = this.get_scaled_y(node1);
        let y2 = this.get_scaled_y(node2);
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2)
        ctx.stroke()
        ctx.fill();

        if (this.is_mouse_in_stoke(ctx)) {
          edge.is_hovered = true
          this.is_edge_hovered = true
        } else {
          edge.is_hovered = false

        }

      }
      ctx.globalAlpha = 1;

    }

  }


}
