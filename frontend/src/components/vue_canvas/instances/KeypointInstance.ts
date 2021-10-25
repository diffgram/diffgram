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
  public occluded: boolean = false;
  public is_bounding_box_hovered: boolean = false;
  public is_dragging_instance: boolean = false;
  public template_creation_mode: boolean = false; // Set this to allow the creation of new nodes and edges.
  public node_hover_index: any = undefined;
  public center: any = undefined;
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
  public mouse_down_position: any = undefined;
  public initialized: boolean = false;
  public current_node_connection: any = [];
  public instance_rotate_control_mouse_hover: boolean = undefined
  public angle: number = 0
  public label_settings: any = undefined
  private nearest_points_dict: any = undefined


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
    this.nodes = [];
    this.edges = [];
    this.on_instance_updated = on_instance_updated;
    this.on_instance_selected = on_instance_selected;
    this.on_instance_deselected = on_instance_deselected;
    this.mouse_down_delta_event = mouse_down_delta_event;
    this.mouse_down_position = mouse_down_position;
    this.instance_context = instance_context;
    this.type = 'keypoints'
    this.mouse_position = mouse_position;
    this.initialized = true;
    this.occluded = false;
    this.ctx = ctx;
    this.label_settings = label_settings;
  }

  public duplicate_for_undo(){
    /*
    * This is used just in the context of undo. Duplicates the entire instance
    * we reference ID version number. This is different from copy/paste as in this context
    * we DO keep the version_id, root_id, creation_ref_id
    * */
    let duplicate_instance = new KeypointInstance(
      this.mouse_position,
      this.ctx,
      this.instance_context,
      this.on_instance_updated,
      this.on_instance_selected,
      this.on_instance_deselected,
      this.mouse_down_delta_event,
      this.mouse_down_position,
      this.label_settings,
    );
    let instance_data_to_keep = {
      ...this,
      nodes: this.nodes.map(n => ({...n}) ),
      edges: this.edges.map(e => ({...e}) ),
    };
    duplicate_instance.populate_from_instance_obj(instance_data_to_keep);
    return duplicate_instance
  }
  public toggle_occluded(node_index){
    // The intial state may be null that's why not using !value
    if (this.nodes[node_index].occluded == true) {
      this.nodes[node_index].occluded = false
    } else {
      this.nodes[node_index].occluded = true
    }
  }
  public set_new_xy_to_scaled_values(): void{
    for(let node of this.nodes){
      if (node.x < 300) {
        node.left_or_right = 'left'
      } else {
        node.left_or_right = 'right'
      }
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
    if(this.selected || (this.is_bounding_box_hovered && this.node_hover_index == undefined)){
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
        this.stop_rotating()
      }

    }

  }

  private do_rotation_movement() {
    this.angle = this.get_angle_of_from_rotation_control_movement()
  }

  private move_single_node(node) {
    let x_move = this.mouse_down_delta_event.x;
    let y_move = this.mouse_down_delta_event.y;
    let old = {...node}
    let old_x =  old.x
    let old_y = old.y
    let new_point = {x: 0, y:0};
    new_point.x = old_x + x_move;
    new_point.y = old_y + y_move;
    node.x = new_point.x
    node.y = new_point.y
    return node
  }

  private drag_instance(event): void{
    for(let node of this.nodes){
      node = this.move_single_node(node)
    }
  }
  public stop_moving(){
    this.is_moving = false;
  }
  public move(){

    if(this.is_rotating == true){
      this.do_rotation_movement()
      this.calculate_min_max_points();
      return true
    }
    else if (this.is_moving) {
      this.move_node(event)
      return true;
    }
    else if(this.is_dragging_instance){
      this.drag_instance(event);
      this.calculate_min_max_points();
      return true
    }
    else{
      return false;
    }
  }

  public get_rotated_min_max(){
    let rotated_nodes = this.nodes.map(node => this.get_rotated_point(node, this.angle))
    let min_x = Math.min(...rotated_nodes.map(n => n.x)) - this.vertex_size;
    let max_x = Math.max(...rotated_nodes.map(n => n.x)) + this.vertex_size;
    let min_y = Math.min(...rotated_nodes.map(n => n.y)) - this.vertex_size;
    let max_y = Math.max(...rotated_nodes.map(n => n.y)) + this.vertex_size;
    return {
      min_x,
      min_y,
      max_x,
      max_y
    }
  }
  public get_center_point_rotated(){
    let min_max_obj = this.get_rotated_min_max()

    let center_x = (min_max_obj.max_x  + min_max_obj.min_x) / 2;
    let center_y = (min_max_obj.min_y + min_max_obj.max_y) / 2;
    return {
      x: center_x, y: center_y
    }
  }

  public calculate_center(){
    // This is the unrotated center.
    let x = (this.x_max + this.x_min) / 2
    let y = (this.y_max + this.y_min) / 2
    this.center_x = parseInt(x.toString())
    this.center_y = parseInt(y.toString())
    this.center = {x: this.center_x, y: this.center_y};
  }
  private move_node(event): void {
    if (this.node_hover_index == undefined) {
      return
    }
    let node = this.nodes[this.node_hover_index]
    if (node) {

      node.x = this.get_rotated_point(this.mouse_position, -this.angle).x
      node.y = this.get_rotated_point(this.mouse_position, -this.angle).y

      this.instance_updated_callback(this);
    }
  }

  private calculate_min_max_points(){
    if (this.nodes) {
      //TODO handle for case where it's rotated and user pushes bounds (causes whole object to move)
      let x_node_unrotated_list = [...this.nodes.map(p => p.x)]
      let y_node_unrotated_list = [...this.nodes.map(p => p.y)]
      this.x_min = parseInt(Math.min(...x_node_unrotated_list).toString()) // careful math.min() expects destructured otherwised NaN
      this.y_min = parseInt(Math.min(...y_node_unrotated_list).toString())
      this.x_max = parseInt(Math.max(...x_node_unrotated_list).toString())
      this.y_max = parseInt(Math.max(...y_node_unrotated_list).toString())
    }
  }

  private get_scaled_and_rotated_point(point){
    let x = this.get_scaled_x(point)
    let y = this.get_scaled_y(point)
    return {'x' : x, 'y' : y}
  }

  private get_scaled_x(point){

    // Origin is center of shape
    let x = this.get_rotated_point(point).x

    if(this.scale_width == undefined){return x }
    if(this.reference_width == undefined){return x}
    if(this.translate_x == undefined){return x}
    return this.translate_x +  (this.scale_width / this.reference_width) * x
  }

  private get_scaled_y(point){
    let y = point.y;
    //let degrees = 90;
    //let angle =  degrees * (Math.PI/180)

    y = this.get_rotated_point(point).y

    if(this.scale_height == undefined){return y}
    if(this.reference_height == undefined){return y}
    if(this.translate_y == undefined){return y}

    return this.translate_y + (this.scale_height/ this.reference_height) * y
  }

  private get_rotate_point_control_location(): {x: number, y: number}{
    // TODO
    let x_node_unrotated_list = [...this.nodes.map(p => p.x)]
    let y_node_unrotated_list = [...this.nodes.map(p => p.y)]
    let x_min = parseInt(Math.min(...x_node_unrotated_list).toString())
    let y_min = parseInt(Math.min(...y_node_unrotated_list).toString())
    let x_max = parseInt(Math.max(...x_node_unrotated_list).toString())
    let y_max = parseInt(Math.max(...y_node_unrotated_list).toString())

    let center_x = (x_max + x_min) / 2;
    let center_y = (y_max +  y_min) / 2;

    let center_point =  {
      x: center_x,
      y: center_y + (this.height)
    }
    let rotated_center_point = this.get_scaled_and_rotated_point(center_point);
    return rotated_center_point
  }

  private get_rotated_point(
      point,
      angle = undefined,
      origin = undefined): { x: number, y: number }{

    // https://stackoverflow.com/questions/2259476/rotating-a-point-about-another-point-2d
    if (angle === undefined){
      angle = this.angle
    }

    if (origin === undefined) {
      origin = this.center;
    }

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

  private get_angle_of_from_rotation_control_movement () {
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


  public draw_rotate_point(
      ctx,
      is_mouse_in_path,
      radius): boolean {

    if(this.template_creation_mode){
      return
    }
    let rotate_point = this.get_rotate_point_control_location()

    if(!rotate_point){
      return this.instance_rotate_control_mouse_hover
    }
    ctx.beginPath();
    ctx.strokeStyle = 'blue';
    ctx.fillStyle = 'white';
    ctx.lineWidth = '4px';
    ctx.arc(rotate_point.x, rotate_point.y, radius + 5, 0, 2 * Math.PI);
    ctx.fill()
    ctx.stroke()
    if(this.is_mouse_in_path(ctx)){
      this.is_hovered = true
      this.instance_rotate_control_mouse_hover = true
    }
    else if(!this.is_rotating){
      if(!this.is_bounding_box_hovered){
        this.is_hovered = false
      }
      this.instance_rotate_control_mouse_hover = null
    }

    return this.instance_rotate_control_mouse_hover
  }

  private draw_node_label(ctx, node){
    if(!node.name){
      return
    }
    let prevfillStyle = ctx.fillStyle.toString();

    let font_size = 12 / this.ctx.getTransform().a;
    ctx.font = font_size + "px Verdana";
    ctx.textBaseline = 'bottom'

    let message = node.name
    let text_width = ctx.measureText(message).width;

    ctx.fillStyle = "rgba(" + '255, 255, 255,' + '1' + ")";

    let text_height = font_size;
    // the `y - text_height` assumes textBaseline = 'bottom', it's not needed if textBaseline = 'top'
    let padding = 2
    let point = this.get_rotated_point({x: node.x + 5, y: node.y + 5 - text_height - padding });
    let point_text = this.get_rotated_point({x: node.x + 5, y: node.y + 5  });
    ctx.fillRect(
      point.x,
      point.y,
      text_width + padding,
      text_height + padding)

    ctx.fillStyle = "rgba(0,0,0,1)";
    ctx.fillText(message, point.x, point_text.y);



    ctx.fillStyle = prevfillStyle



  }

  public draw(ctx): void {
    this.ctx = ctx;
    this.num_hovered_paths = 0;
    let i = 0;
    // Not sure where we want to set this
    this.width = this.x_max - this.x_min
    this.height = this.y_max - this.y_min

    this.calculate_center()

    this.draw_instance_bounding_box(ctx)

    this.draw_rotate_point(ctx, this.is_mouse_in_path, this.vertex_size)
    // Draw current edge
    this.draw_currently_drawing_edge(ctx)

    this.draw_edges(ctx)

    this.nearest_points_dict = {}

    for (let node of this.nodes) {
      // order of operations
      ctx.lineWidth = 2;

      if (this.label_settings &&
          this.label_settings.show_occluded_keypoints == false &&
          node.occluded == true) {
        continue
      }

      if (node.occluded == true) {
        ctx.fillStyle = 'gray'
      } else {
        ctx.strokeStyle = this.strokeColor;
        ctx.fillStyle = this.fillColor;
      }


      let x = node.x
      let y = node.y

      x = this.get_scaled_x(node)
      y = this.get_scaled_y(node)

      this.draw_point_and_set_node_hover_index(x, y, i, ctx)

      this.draw_node_label(ctx, node);

      this.draw_left_right_arrows(ctx, node, x, y)

      i += 1
    }
    this.draw_rotate_point(ctx, this.is_mouse_in_path, this.vertex_size)
    this.determine_and_set_nearest_node_hovered(ctx)

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

  private determine_and_set_nearest_node_hovered(ctx){
    const sorted_keys = Object.keys(this.nearest_points_dict).map(elm => parseFloat(elm)).sort(function(a,b) { return a - b;})
    const sorted: any[] =  sorted_keys.reduce(
        (obj, key): any => {
          obj[key.toString()] = this.nearest_points_dict[key.toString()];
          return obj;
        },
        {}
    );

    if(!sorted || sorted.length === 0){
      return
    }
    let index = parseInt(this.nearest_points_dict[Object.keys(sorted)[0]])
    if(this.nodes[index] == undefined){
      return
    }
    let point = {'x': this.nodes[index].x, 'y': this.nodes[index].y}
    let radius = this.vertex_size + 10

    if (this.point_is_intersecting_circle(
      this.get_scaled_and_rotated_point(point),
      this.mouse_position,
      radius))
    {
      this.set_node_hovered(ctx, index)
    }
  }
  private draw_left_right_arrows(ctx, node, x, y){
    if (this.label_settings &&
        this.label_settings.show_left_right_arrows == false) {
      return
    }
    let size = this.vertex_size * 8
    if(node.left_or_right == 'left') {
      this.draw_icon(ctx, x - 5, y, 'arrow_left', size, 'rgb(255,0,0)')
    }
    if(node.left_or_right=='right') {
      this.draw_icon(ctx, x + 5, y, 'arrow_right', size, 'rgb(0,255,0)')
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
    if (this.is_node_hovered) {
      if (this.current_node_connection.length === 1) {
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
        id: uuidv4(),
        occluded: undefined,
        left_or_right: undefined
      })
    }
  }

  private draw_icon(
        ctx, x, y, icon='arrow_left',
        font_size=24, fillStyle='rgb(255,175,0)'){
    // CAUTION if icon is invalid it won't render anything
    // use `arrow_left` as an example that works
    if(!ctx.material_icons_loaded){
      return
    }
    const old_color = ctx.fillStyle;
    const old_font = ctx.font
    const old_textAlign = ctx.textAlign
    const old_baseLine = ctx.textBaseline

    ctx.font = font_size + 'px material-icons'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    const text_icon = icon;
    //outline
    ctx.font = font_size + 'px material-icons'
    ctx.fillStyle = 'rgb(255,255,255)'
    const text = ctx.fillText(
      text_icon,
      x,
      y);

    // inset main
    let border_width = Math.round(font_size / 3)
    ctx.fillStyle = fillStyle
    ctx.font = font_size - border_width + 'px material-icons'
    ctx.fillText(
      text_icon,
      x,
      y);

    ctx.fillStyle = old_color;
    ctx.font = old_font;
    ctx.textAlign = old_textAlign
    ctx.textBaseline = old_baseLine
    //const measures = ctx.measureText(text_icon);
    // Create an invisible box for click events.
    //const region = {x: x - 24 , y: y - 24 , w: measures.width, h: 100};
    //this.is_mouse_in_path_issue(ctx, region, i, issue)
    return true
  }

  private is_mouse_in_path(ctx) {
    if(!this.mouse_position || !this.mouse_position.raw){
      return false
    }
    if (ctx.isPointInPath(
      this.mouse_position.raw.x,
      this.mouse_position.raw.y)) {
      return true;
    }
    return false

  }
  private draw_instance_bounding_box(ctx){
    let min_max_obj = this.get_rotated_min_max();
    let width = Math.abs(min_max_obj.max_x - min_max_obj.min_x);
    let height = Math.abs(min_max_obj.max_y - min_max_obj.min_y);

    ctx.globalAlpha = 0.4;
    ctx.beginPath();

    ctx.rect(min_max_obj.min_x, min_max_obj.min_y, width + this.vertex_size, height + this.vertex_size);
    if(this.selected){
      ctx.stroke()
      ctx.fill()
    }


    if(this.is_mouse_in_path(ctx)){
      this.is_bounding_box_hovered = true;
      this.is_hovered = true;
      // Draw helper bounding box
      if(!this.selected){
        ctx.fillStyle = 'white'
        ctx.globalAlpha = 0.2;
        ctx.stroke()
        ctx.fill()
      }
    }
    else{
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
    ctx.fillStyle = 'green'
    this.num_hovered_paths += 1
  }

  private draw_point_and_set_node_hover_index(x, y, i, ctx): void {
    ctx.beginPath();
    if(this.node_hover_index === i){
      ctx.fillStyle = 'green'
    }
    ctx.arc(x, y, this.vertex_size, 0, 2 * Math.PI);
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

      if (node2.occluded == true) {
        ctx.strokeStyle = 'gray'
      }
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
