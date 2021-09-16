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
  public is_rotating: boolean = false;
  public scale_width: number = undefined;
  public scale_height: number = undefined;
  public translate_x: number = undefined;
  public translate_y: number = undefined;
  public reference_width: number = undefined;
  public reference_height: number = undefined;
  public mouse_down_delta_event: any = undefined;
  public initialized: boolean = false;
  public current_node_connection: any = [];
  private instance_rotate_control_mouse_hover: boolean = undefined
  public angle: number = 0


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
      node.x = this.get_scaled_x(node);
      node.y = this.get_scaled_y(node);
    }
    this.scale_height = undefined;
    this.scale_width = undefined;
    this.translate_y = undefined;
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
    if(this.instance_rotate_control_mouse_hover == true){
      this.is_rotating = true
    }
  }

  public stop() {

    if (this.instance_context.draw_mode
    && this.template_creation_mode) {
      this.add_node_to_instance();
    }
    else {
      if(this.is_moving){
        this.stop_moving();
      }
      if(this.node_hover_index != undefined){
        this.select();
      }

      if(this.is_dragging_instance){
        this.stop_dragging()
      }

      if(this.is_rotating == true) {
        this.is_rotating = false
      }

    }

  }

  private do_rotation_movement() {
    this.angle = this.get_angle_of_from_rotation_control_movement()
    var pi = Math.PI;
    let degrees = this.angle  * (180/pi);
    console.log('ANGLEEE', this.angle, degrees)
    //console.log(this.angle)
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
    if(this.is_rotating == true){
      this.do_rotation_movement()
      return true
    }
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

  private get_scaled_x(point){
    //console.log(this.scale_width, this.reference_width, this.translate_x)
    let x = point.x
    //let degrees = 90;
    //let angle =  degrees * (Math.PI/180)
    // Origin is center of shape

    let angle = this.angle

    let origin = {
      x: (this.x_max + this.x_min) / 2,
      y: (this.y_max + this.y_min) / 2,
    }
    x = this.get_rotated_point(origin, point, angle).x

    if(this.scale_width == undefined){return x }
    if(this.reference_width == undefined){return x}
    if(this.translate_x == undefined){return x}
    return this.translate_x +  (this.scale_width / this.reference_width) * x
  }

  private get_scaled_y(point){
    let y = point.y;
    //let degrees = 90;
    //let angle =  degrees * (Math.PI/180)
    let angle = this.angle

    let origin = {
      x: (this.x_max + this.x_min) / 2,
      y: (this.y_max + this.y_min) / 2,
    }

    y = this.get_rotated_point(origin, point, angle).y

    if(this.scale_height == undefined){return y}
    if(this.reference_height == undefined){return y}
    if(this.translate_y == undefined){return y}

    return this.translate_y + (this.scale_height/ this.reference_height) * y
  }

  private get_rotate_point(){
    let x_top = this.x_max
    let y_top = this.y_max
    let v = {x: this.center_x - x_top, y: this.center_y - y_top};
    let v_len = Math.sqrt( v.x ** 2 + v.y ** 2);
    let u = {x: v.x / v_len, y: v.y / v_len};
    // return {
    //   x: x_top - 80 * (u.x),  // The point along a line at a distance d (d=20) is => (x0, y0) + d*u
    //   y: y_top - 80 * (u.y)
    // }
    return {
      x: this.center_x,
      y: this.center_y + (this.height) - 20
    }
  }

  private get_rotated_point(origin, point, angle){
    // https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d
    // Move point to origin
    let _px = point.x - origin.x
    let _py = point.y - origin.y
    // Rotate points
    let qx = (Math.cos(angle) * _px) - (Math.sin(angle) * _py)
    let qy = (Math.sin(angle) * _px) + (Math.cos(angle) * _py)
    // Move back to original position
    qx = origin.x + qx
    qy = origin.y + qy
    return {x: qx, y: qy}
  }
  private get_x_of_rotated_point(t, instance, h, angle=undefined){
    let rot_angle = angle != undefined ? angle : instance.angle ;
    let a = instance.width;
    let b = instance.height;
    let x = h + a*Math.cos(t) * Math.cos(rot_angle) - b * Math.sin(t) * Math.sin(rot_angle)
    return x
  }

  private get_t(instance) {

    let a = instance.width;
    let b = instance.height;
    let t = Math.atan(-(b) *  Math.tan(instance.angle))/ (a);
    return t
  }


  private get_y_of_rotated_point(t, instance, k, angle=undefined){
    let rot_angle = angle != undefined ? angle : instance.angle ;
    let a = instance.width;
    let b = instance.height;
    let y = k + b*Math.sin(t) * Math.cos(rot_angle) + a * Math.cos(t) * Math.sin(rot_angle)
    return y
  }

  private get_angle_of_from_rotation_control_movement () {
    // Read: https://math.stackexchange.com/questions/361412/finding-the-angle-between-three-points

    let a = this.width;
    let b = this.height;
    let t = Math.atan(-(b) *  Math.tan(0))/ (a);
    let centered_x = this.get_x_of_rotated_point(t, this, 0)
    let centered_y = this.get_y_of_rotated_point(t, this, 0)
    let A = {x: centered_x, y: centered_y}
    let B = {x: this.center_x, y: this.center_y}
    let C = {x: this.mouse_position.x, y: this.mouse_position.y}
    let BA = {x: A.x - B.x, y: A.y - B.y}
    let BC = {x: C.x - B.x, y: C.y - B.y}
    let BA_len = Math.sqrt((BA.x ** 2) + (BA.y ** 2))
    let BC_len = Math.sqrt((BC.x ** 2) + (BC.y ** 2))
    let BA_dot_BC = (BA.x * BC.x) + (BA.y * BC.y)
    let theta = Math.acos(BA_dot_BC / (BA_len * BC_len))
    let angle = 0;
    if(this.mouse_position.y < B.y){
      angle = (Math.PI /2)  - theta
    }
    else{
      if(theta <= (Math.PI/2) && theta > 0){
        // First cuadrant.
        angle = (Math.PI /2)  + theta
      }
      else if(theta > (Math.PI/2) && theta > 0){
        // Second Cuadrant
        angle = (Math.PI /2)  + theta
      }
    }
    //console.log(angle)
    return angle;
  }


  private set_instance_color(){

  }

  private draw_rotate_point(
      ctx,
      draw_single_path_circle,
      is_mouse_in_path,
      i,
      radius): boolean {

    this.instance_rotate_control_mouse_hover = null

    let rotate_point = this.get_rotate_point()

    draw_single_path_circle(
        rotate_point.x,
        rotate_point.y ,
        radius + 4, ctx, 'blue', '4px')
    if(is_mouse_in_path(ctx, i, this)){
      this.instance_rotate_control_mouse_hover = true
    }

    return this.instance_rotate_control_mouse_hover
  }

  public draw(ctx): void {
    this.ctx = ctx;
    this.num_hovered_paths = 0;
    let i = 0;

    // Not sure where we want to set this
    this.width = this.x_max - this.x_min
    this.height = this.y_max - this.y_min

    this.center_x = parseInt(this.x_max - (this.width / 2))
    this.center_y = parseInt(this.y_max - (this.height / 2))

    this.draw_instance_bounding_box(ctx)

    // Draw current edge
    this.draw_currently_drawing_edge(ctx)

    this.draw_edges(ctx)

    for (let node of this.nodes) {
      // order of operations
      ctx.lineWidth = 2;
      ctx.strokeStyle = this.strokeColor;
      ctx.fillStyle = this.fillColor;
      let x = node.x
      let y = node.y

      x = this.get_scaled_x(node)
      y = this.get_scaled_y(node)
      //console.log(this)

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

  public stop_rotating(){
    this.is_rotating = false
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
        let x1 = this.get_scaled_x(node1);
        let x2 = this.get_scaled_x(node2);
        let y1 = this.get_scaled_y(node1);
        let y2 = this.get_scaled_y(node2);
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2)
        ctx.stroke()
        ctx.fill();
      }


    }
  }


}
