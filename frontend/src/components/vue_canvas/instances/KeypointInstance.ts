import {InstanceBehaviour, Instance} from './Instance'
import {InstanceContext} from './InstanceContext';
import {v4 as uuidv4} from 'uuid';

export class KeypointInstance extends Instance implements InstanceBehaviour {
  public mouse_position: any;
  public ctx: CanvasRenderingContext2D;
  private vertex_size: number = 5;
  private line_width: number = 2;
  public strokeColor: string = 'black';
  public fillColor: string = 'white';
  public instance_context: InstanceContext = undefined;
  public is_hovered: boolean = false; // Is true if any of the nodes or bounding box is being hovered.
  public is_node_hovered: boolean = false;
  public is_bounding_box_hovered: boolean = false;
  public is_dragging_instance: boolean = false;
  public template_creation_mode: boolean = false; // Set this to allow the creation of new nodes and edges.
  public node_hover_index: any = undefined;
  public num_hovered_paths: number = 0;
  public is_drawing_edge: boolean = false;
  public is_moving: boolean = false;
  public scale_width: number = undefined;
  public scale_height: number = undefined;
  public translate_x: number = undefined;
  public translate_y: number = undefined;
  public reference_width: number = undefined;
  public reference_height: number = undefined;
  public mouse_down_delta_event: any = undefined;
  public initialized: boolean = false;
  public current_node_connection: any = [];

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
              mouse_down_delta_event = undefined) {

    super();
    this.nodes = [];
    this.edges = [];
    this.on_instance_updated = on_instance_updated;
    this.on_instance_selected = on_instance_selected;
    this.on_instance_deselected = on_instance_deselected;
    this.mouse_down_delta_event = mouse_down_delta_event;
    this.instance_context = instance_context;
    this.type = 'keypoints'
    this.mouse_position = mouse_position;
    this.initialized = true;
    this.ctx = ctx;
  }
  public set_new_xy_to_scaled_values(): void{
    for(let node of this.nodes){
      node.x = this.get_scaled_x(node.x);
      node.y = this.get_scaled_y(node.y);
    }
    this.scale_height = undefined;
    this.scale_width = undefined;
    this.translate_y = undefined;
    this.translate_x = undefined;
    this.translate_x = undefined;
    this.reference_width = undefined;
    this.reference_height = undefined;
  }

  public contextmenu(event): void {
  }

  public double_click(event): void {
    if (!this.is_hovered) {
      return
    }
    if (this.node_hover_index == undefined) {
      return
    }
    let node = this.nodes[this.node_hover_index]
    let new_edges = this.edges.filter(edge => {
      if (edge.from === node.id || edge.to === node.id) {
        return false
      } else {
        return true
      }
    })
    this.nodes.splice(this.node_hover_index, 1);
    this.edges = new_edges;
    this.current_node_connection = []
  }
  public start_movement(): void{
    if (this.node_hover_index != undefined) {
      this.is_moving = true;
    }
    if(this.selected && this.is_bounding_box_hovered){
      this.start_dragging();
    }
  }

  private drag_instance(event): void{
    let x_move = this.mouse_down_delta_event.x;
    let y_move = this.mouse_down_delta_event.y;
    for(let node of this.nodes){
      node.x += x_move;
      node.y += y_move;
      node.x = parseInt(node.x)
      node.y = parseInt(node.y)
    }
  }
  public stop_moving(){
    this.is_moving = false;
  }
  public move(){
    if (this.is_moving) {
      this.move_node(event)
      return true;
    }
    else if(this.is_dragging_instance){
      this.ctx.canvas.style.cursor = 'all-scroll'
      this.drag_instance(event);
      return true
    }
    else{
      return false;
    }
  }

  private get_scaled_x(x){
    if(this.scale_width == undefined){return x }
    if(this.reference_width == undefined){return x}
    if(this.translate_x == undefined){return x}
    return this.translate_x +  (this.scale_width / this.reference_width) * x
  }


  private get_scaled_y(y){
    if(this.scale_height == undefined){return y}
    if(this.reference_height == undefined){return y}
    if(this.translate_y == undefined){return y}
    return this.translate_y + (this.scale_height/ this.reference_height) * y
  }
  private set_instance_color(){

  }
  public draw(ctx): void {
    this.ctx = ctx;
    this.num_hovered_paths = 0;
    let i = 0;
    this.draw_instance_bounding_box(ctx)

    // Draw current edge
    this.draw_currently_drawing_edge(ctx)

    this.draw_edges(ctx)

    for (let node of this.nodes) {
      ctx.lineWidth = 2;
      ctx.strokeStyle = this.strokeColor;
      ctx.fillStyle = this.fillColor;
      let x = this.get_scaled_x(node.x);
      let y = this.get_scaled_y(node.y);
      this.draw_point(x, y, i, ctx)
      i += 1
    }
    if (this.num_hovered_paths === 0) {
      this.node_hover_index = undefined;
      this.is_node_hovered = false;
    }

    if(this.num_hovered_paths > 0 || this.is_bounding_box_hovered){
      this.is_hovered = true;
    }
    if(this.num_hovered_paths === 0 && !this.is_bounding_box_hovered){
      if(this.is_hovered){
        this.is_hovered = false;
      }
    }


  }

  private move_node(event): void {
    if (this.node_hover_index == undefined) {
      return
    }
    let node = this.nodes[this.node_hover_index]
    if (node) {
      node.x = this.mouse_position.x
      node.y = this.mouse_position.y
      this.instance_updated_callback(this);
    }
  }
  public stop_dragging(){
    this.is_dragging_instance = false;
  }

  public start_dragging(){
    this.is_dragging_instance = true;
  }
  public add_node_to_instance() {
    if (this.is_hovered) {
      if (this.current_node_connection.length === 1) {
        //console.log('aaaa ad edgeee', this.node_hover_index, this.current_node_connection)
        if(this.node_hover_index == undefined){return}
        let node = this.nodes[this.node_hover_index];
        this.current_node_connection.push(node);
        this.is_drawing_edge = false
        this.edges.push({
          from: this.current_node_connection[0].id,
          to: this.current_node_connection[1].id,
        })
        this.current_node_connection = [];
        this.is_drawing_edge = false;
      } else if (this.current_node_connection.length === 0) {
        //console.log('11aaaa ad edgeee', this.node_hover_index, this.current_node_connection)
        if(this.node_hover_index == undefined){return}
        let node = this.nodes[this.node_hover_index];
        this.current_node_connection.push(node);
        this.is_drawing_edge = true;
      }

    } else {
      if (this.is_drawing_edge) {
        return
      }
      this.nodes.push({
        x: this.mouse_position.x,
        y: this.mouse_position.y,
        id: uuidv4()
      })
    }
  }


  private is_mouse_in_path(ctx) {
    if (ctx.isPointInPath(
      this.mouse_position.raw.x,
      this.mouse_position.raw.y)) {
      return true;
    }
    return false

  }
  private draw_instance_bounding_box(ctx){
    if(!this.selected){ return }

    let min_x = Math.min(...this.nodes.map(n => n.x)) - this.vertex_size
    let max_x = Math.max(...this.nodes.map(n => n.x)) + this.vertex_size
    let min_y = Math.min(...this.nodes.map(n => n.y)) - this.vertex_size
    let max_y = Math.max(...this.nodes.map(n => n.y)) + this.vertex_size
    let width = Math.abs(max_x - min_x);
    let height = Math.abs(max_y - min_y);

    ctx.globalAlpha = 0.4;
    ctx.beginPath();
    ctx.rect(min_x, min_y, width + this.vertex_size, height + this.vertex_size);
    ctx.stroke()
    ctx.fill()
    if(this.is_mouse_in_path(ctx)){
      this.is_bounding_box_hovered = true;
      this.is_hovered = true;
    }
    else{
      this.is_bounding_box_hovered = false;
    }
    ctx.globalAlpha = 1;
  }

  private draw_point(x, y, i, ctx): void {
    ctx.beginPath();
    ctx.arc(x, y, this.vertex_size, 0, 2 * Math.PI);
    if (this.is_mouse_in_path(ctx)) {
      this.is_hovered = true;
      this.is_node_hovered = true;
      this.node_hover_index = i
      ctx.fillStyle = 'green'
      this.num_hovered_paths += 1

    }
    ctx.stroke();
    ctx.fill();
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
    ctx.beginPath();
    ctx.lineWidth = 2;
    ctx.setLineDash([])
    ctx.moveTo(this.current_node_connection[0].x, this.current_node_connection[0].y);
    ctx.lineTo(this.mouse_position.x, this.mouse_position.y)
    ctx.stroke()
    ctx.fill();

  }

  private draw_edges(ctx) {
    ctx.lineWidth = this.line_width;
    ctx.setLineDash([])
    ctx.beginPath();
    for (let edge of this.edges) {
      let node1 = this.nodes.filter(n => n.id === edge.from)[0];
      let node2 = this.nodes.filter(n => n.id === edge.to)[0];
      if(node1 && node2){
        let x1 = this.get_scaled_x(node1.x);
        let x2 = this.get_scaled_x(node2.x);
        let y1 = this.get_scaled_y(node1.y);
        let y2 = this.get_scaled_y(node2.y);
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2)
        ctx.stroke()
        ctx.fill();
      }


    }
  }


}
