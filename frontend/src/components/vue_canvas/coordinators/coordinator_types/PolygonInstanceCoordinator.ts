import {Coordinator, CoordinatorProcessResult} from "../../../../../embed/src/types/coordinators/Coordinator";
import {
  InteractionEvent,
  ImageAnnotationEventCtx,
  ImageInteractionEvent
} from "../../../../../embed/src/types/annotation/InteractionEvent";
import {ImageAnnotationCoordinator} from "./ImageAnnotationCoordinator";
import {CanvasMouseCtx, Point, point_is_intersecting_circle} from "../../../../types/mouse_position";
import CommandManager from "../../../../helpers/command/command_manager";
import {PolygonInstance, PolygonPoint} from "../../../../../embed/src/types/instances/PolygonInstance";
import {BoxInstance} from "../../instances/BoxInstance";
import {PolygonAutoBorderTool} from "../../../../../embed/src/types/annotation/image/advanced_tools/PolygonAutoBorderTool";
import {GLOBAL_SELECTED_COLOR} from "../../instances/Instance";
import {InstanceImage2D} from "../../../../../embed/src/types/instances/InstanceImage2D";

export class PolygonInstanceCoordinator extends ImageAnnotationCoordinator {
  /**
   * Routes an annotation_event and interaction of a user to box instances.
   * */
  public snap_to_edges_num_pixels: number = 5
  public auto_border_polygon_p1: PolygonPoint = null
  public auto_border_polygon_p2: PolygonPoint = null

  constructor(poly_instance, canvas_mouse_ctx: CanvasMouseCtx, command_manager: CommandManager) {
    super();
    this.instance = poly_instance
    this.canvas_mouse_ctx = canvas_mouse_ctx
    this.command_manager = command_manager
  }

  private should_start_drawing(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_down_event(annotation_event) &&
      !annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
  }

  private should_set_autoborder_point_index(annotation_event: ImageInteractionEvent) {
    return this.is_mouse_down_event(annotation_event) &&
      annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
  }


  private polygon_auto_border_set_indexes(result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    const auto_border_tool = new PolygonAutoBorderTool(annotation_event.annotation_ctx.auto_border_context);
    const current_poly = annotation_event.annotation_ctx.current_drawing_instance as PolygonInstance;
    let instance_list = annotation_event.annotation_ctx.instance_list
    auto_border_tool.polygon_auto_border_set_indexes(instance_list, current_poly)
    result.auto_border_context = auto_border_tool.context
  }
  private should_move_polygon_points(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_move_event(annotation_event) &&
      !annotation_event.annotation_ctx.is_actively_drawing
      && !annotation_event.annotation_ctx.draw_mode
      && annotation_event.annotation_ctx.polygon_point_click_index != undefined
      && annotation_event.annotation_ctx.canvas_mouse_tools.mouse_is_down
  }

  private should_drag_polygon(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_move_event(annotation_event) &&
      !annotation_event.annotation_ctx.is_actively_drawing
      && !annotation_event.annotation_ctx.draw_mode
      && annotation_event.annotation_ctx.locked_editing_instance
      && annotation_event.annotation_ctx.locked_editing_instance.selected
      && annotation_event.annotation_ctx.polygon_point_click_index == undefined
      && annotation_event.annotation_ctx.canvas_mouse_tools.mouse_is_down
  }

  private should_stop_drag_polygon(annotation_event: ImageInteractionEvent): boolean {
    let poly = annotation_event.annotation_ctx.locked_editing_instance as PolygonInstance
    return this.is_mouse_up_event(annotation_event) &&
      poly &&
      poly.selected &&
      poly.is_moving &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode


  }

  private drag_polygon(result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    const poly = annotation_event.annotation_ctx.locked_editing_instance as PolygonInstance
    if (!poly.selected) {
      return;
    }
    let x_move = annotation_event.annotation_ctx.mouse_down_delta_event.x;
    let y_move = annotation_event.annotation_ctx.mouse_down_delta_event.y;
    poly.move_polygon_points(x_move, y_move, poly.hovered_figure_id)
    result.instance_moved = true
    result.locked_editing_instance = poly

  }

  private should_start_moving_polygon_points(annotation_event: ImageInteractionEvent): boolean {
    let poly = this.instance as PolygonInstance
    return this.is_mouse_down_event(annotation_event) &&
      poly &&
      poly.polygon_point_hover_index != undefined &&
      !poly.soft_delete &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private should_start_dragging_polygon(annotation_event: ImageInteractionEvent): boolean {
    let poly = this.instance as PolygonInstance
    return this.is_mouse_down_event(annotation_event) &&
      poly &&
      poly.polygon_point_hover_index == undefined &&
      poly.is_hovered &&
      !poly.soft_delete &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private should_detect_polygon_point(annotation_event: ImageInteractionEvent): boolean {
    let poly = this.instance as PolygonInstance
    return this.is_mouse_move_event(annotation_event) &&
      poly &&
      poly.selected &&
      !poly.soft_delete &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private should_insert_polygon_midpoint(annotation_event: ImageInteractionEvent): boolean {
    let poly = this.instance as PolygonInstance
    return this.is_mouse_down_event(annotation_event) &&
      poly &&
      poly.selected &&
      poly.midpoint_hover != undefined &&
      !poly.soft_delete &&
      !annotation_event.annotation_ctx.is_actively_drawing &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private polygon_should_delete_point(annotation_event: ImageInteractionEvent): boolean {
    let poly = this.instance as PolygonInstance
    return this.is_mouse_double_click_event(annotation_event) &&
      poly &&
      poly.selected &&
      !poly.soft_delete &&
      poly.polygon_point_hover_index != undefined
    !annotation_event.annotation_ctx.is_actively_drawing &&
    !annotation_event.annotation_ctx.draw_mode &&
    !annotation_event.annotation_ctx.view_issue_mode &&
    !annotation_event.annotation_ctx.instance_select_for_issue &&
    !annotation_event.annotation_ctx.view_only_mode
  }

  public polygon_delete_point(result: CoordinatorProcessResult, point_index: number = undefined) {
    let instance = this.instance as PolygonInstance
    let index_to_delete = point_index
    if (index_to_delete == undefined) {
      index_to_delete = instance.polygon_point_hover_index
    }
    instance.delete_point(index_to_delete)
    result.instance_moved = true
  }

  public insert_polygon_midpoint(result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    let instance = this.instance as PolygonInstance
    let points = instance.points.map((p) => ({...p}));

    let rest_of_points = [];
    if (instance.hovered_figure_id) {
      points = instance.points.filter(
        (p) => p.figure_id === instance.hovered_figure_id
      );
      rest_of_points = instance.points.filter(
        (p) => p.figure_id !== instance.hovered_figure_id
      );
    }
    let midpoints_polygon = instance.midpoints_polygon;
    if (instance.hovered_figure_id) {
      midpoints_polygon = instance.midpoints_polygon[instance.hovered_figure_id] as PolygonPoint[];
    }

    let new_point_to_add = midpoints_polygon[instance.midpoint_hover] as PolygonPoint;
    if (new_point_to_add == undefined) {
      return;
    }
    points.splice(instance.midpoint_hover + 1, 0, {
      ...new_point_to_add,
      figure_id: instance.hovered_figure_id,
    });

    instance.polygon_point_hover_index = instance.midpoint_hover + 1;
    result.polygon_point_click_index = instance.midpoint_hover + 1;
    // this.polygon_click_index = this.selected_instance_index;

    let hovered_point = points[instance.polygon_point_hover_index];
    if (!hovered_point) {
      return;
    }
    hovered_point.selected = true;
    result.lock_point_hover_change = true;
    instance.midpoint_hover = undefined;
    instance.selected = true;
    if (instance.hovered_figure_id) {
      instance.points = points.concat(rest_of_points);
    } else {
      instance.points = points;
    }
    // this.instance_list.splice(this.selected_instance_index, 1, instance);
  }

  private detect_polygon_midpoints() {
    let poly = this.instance as PolygonInstance
    poly.detect_hover_polygon_midpoints()
  }

  private start_polygon_point_move(result: CoordinatorProcessResult) {
    let poly = this.instance as PolygonInstance
    let original_instance = this.save_original_instance_for_undo()

    poly.set_is_moving(true)
    result.locked_editing_instance = poly
    result.polygon_point_click_index = poly.polygon_point_hover_index
    result.original_edit_instance = original_instance

  }

  private start_polygon_drag(result: CoordinatorProcessResult) {
    let poly = this.instance as PolygonInstance
    let original_instance = this.save_original_instance_for_undo()

    poly.set_is_moving(true)
    result.locked_editing_instance = poly
    result.original_edit_instance = original_instance

  }

  private save_original_instance_for_undo(): PolygonInstance {

    let poly = this.instance as PolygonInstance
    const original_edit_instance = poly.duplicate_for_undo()
    return original_edit_instance
  }

  private should_stop_move_polygon_points(annotation_event: ImageInteractionEvent): boolean {
    let polygon = annotation_event.annotation_ctx.locked_editing_instance as PolygonInstance
    return this.is_mouse_up_event(annotation_event) &&
      polygon &&
      polygon.selected &&
      polygon.is_moving &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private stop_polygon_move(result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    let poly = result.locked_editing_instance as PolygonInstance
    poly.set_is_moving(false)
    this.edit_instance_command_creation(annotation_event, result)
    result.locked_editing_instance = null
    result.polygon_point_click_index = null

  }

  private move_polygon_points(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    let instance = this.instance
    var polygon_point_click_index = annotation_event.annotation_ctx.polygon_point_click_index;

    if (instance && instance.points && instance.points[polygon_point_click_index]) {
      let x_new = annotation_event.annotation_ctx.mouse_position.x;
      let y_new = annotation_event.annotation_ctx.mouse_position.y;
      instance.points[polygon_point_click_index].x = Math.ceil(x_new);
      instance.points[polygon_point_click_index].y = Math.ceil(y_new);

      coordinator_result.instance_moved = true
    }
  }

  private start_polygon_draw(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    this.initialize_instance_drawing(coordinator_result, annotation_event)
    let polygons = annotation_event.annotation_ctx.instance_list.filter(inst => inst.type === 'polygon')
    for(let i = 0; i < polygons.length; i++){
      let poly = polygons[i] as PolygonInstance
      poly.show_polygon_vertices()
    }
  }

  private should_add_polygon_point(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_up_event(annotation_event) &&
      annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
      && !annotation_event.annotation_ctx.auto_border_context.auto_border_polygon_p2_index

  }

  private should_finish_polygon_draw_hotkey(annotation_event: ImageInteractionEvent){
    return this.is_keyup_enter_event(annotation_event) &&
      annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
      && annotation_event.annotation_ctx.current_drawing_instance.points.length > 2
  }


  private polygon_point_limits(annotation_event: ImageInteractionEvent, current_point: PolygonPoint) {
    let is_actively_drawing = annotation_event.annotation_ctx.is_actively_drawing
    let autoborder_context = annotation_event.annotation_ctx.auto_border_context
    let canvas_width = annotation_event.annotation_ctx.canvas_transform.canvas_width
    let canvas_height = annotation_event.annotation_ctx.canvas_transform.canvas_height
    // Set Autoborder point if exists
    if (
      is_actively_drawing &&
      autoborder_context.auto_border_polygon_p1 &&
      !autoborder_context.auto_border_polygon_p2
    ) {
      current_point.x = autoborder_context.auto_border_polygon_p1.x;
      current_point.y = autoborder_context.auto_border_polygon_p1.y;
      current_point.point_set_as_auto_border = true;
    }
    if (is_actively_drawing && autoborder_context.auto_border_polygon_p1 && autoborder_context.auto_border_polygon_p2) {
      current_point.x = autoborder_context.auto_border_polygon_p2.x;
      current_point.y = autoborder_context.auto_border_polygon_p2.y;
      current_point.point_set_as_auto_border = true;
    }
    // TODO look at if this should be 0 or 1  and width or width -1
    if (current_point.x <= this.snap_to_edges_num_pixels) {
      current_point.x = 1;
    }
    if (current_point.y <= this.snap_to_edges_num_pixels) {
      current_point.y = 1;
    }
    if (current_point.x >= canvas_width - this.snap_to_edges_num_pixels) {
      current_point.x = canvas_width - 1;
    }
    if (current_point.y >= canvas_height - this.snap_to_edges_num_pixels) {
      current_point.y = canvas_height - 1;
    }
    return current_point;
  }

  private should_use_turbo_mode(annotation_event: ImageInteractionEvent): boolean {
    let current_polygon_point_list = annotation_event.annotation_ctx.current_drawing_instance.points
    return this.is_mouse_move_event(annotation_event) &&
      annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.shift_key
      && current_polygon_point_list.length >= 1
      && annotation_event.annotation_ctx.draw_mode
  }

  private check_point_canvas_limits(point: Point, canvas_width: number, canvas_height: number): PolygonPoint {
    let result = point as PolygonPoint
    if (point.x <= this.snap_to_edges_num_pixels) {
      result.x = 1;
    }
    if (point.y <= this.snap_to_edges_num_pixels) {
      result.y = 1;
    }
    if (
      point.x >=
      canvas_width - this.snap_to_edges_num_pixels
    ) {
      result.x = canvas_width - 1;
    }
    if (
      point.y >=
      canvas_height - this.snap_to_edges_num_pixels
    ) {
      result.y = canvas_height - 1;
    }
    return result
  }

  private add_point_turbo_mode(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    // this.detect_other_polygon_points();
    let mouse_position = annotation_event.annotation_ctx.mouse_position
    let mouse_down_position = annotation_event.annotation_ctx.mouse_down_position
    let current_polygon_point_list = annotation_event.annotation_ctx.current_drawing_instance.points
    let x_diff = Math.abs(mouse_position.x - current_polygon_point_list[current_polygon_point_list.length - 1].x);
    let y_diff = Math.abs(mouse_position.y - current_polygon_point_list[current_polygon_point_list.length - 1].y)
    if (x_diff > 10 || y_diff > 10) {
      mouse_down_position.x = mouse_position.x;
      mouse_down_position.y = mouse_position.y;
      this.add_polygon_point(coordinator_result, annotation_event);
    }
  }

  private detect_other_polygon_points(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    if (!annotation_event.annotation_ctx.is_actively_drawing) {
      return;
    }
    const polygons_list = annotation_event.annotation_ctx.instance_list.filter(
      (x) => x.type == "polygon"
    );

    for (const polygon of polygons_list) {
      for (const point of polygon.points) {
        if (point_is_intersecting_circle(annotation_event.annotation_ctx.mouse_position, point, 8)) {
          point.hovered_while_drawing = true;
        } else {
          point.hovered_while_drawing = false;
        }
      }
    }
  }

  public finish_drawing_polygon(instance: PolygonInstance, coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    let polygon = annotation_event.annotation_ctx.current_drawing_instance as PolygonInstance
    this.finish_drawing_instance(polygon, coordinator_result, annotation_event)

  }

  private add_polygon_point(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    coordinator_result.is_actively_drawing = true
    let polygon = annotation_event.annotation_ctx.current_drawing_instance as PolygonInstance
    let point = annotation_event.annotation_ctx.mouse_position as PolygonPoint
    point = this.polygon_point_limits(annotation_event, point)
    let corrected_point = this.check_point_canvas_limits(point,
      annotation_event.annotation_ctx.canvas_transform.canvas_width,
      annotation_event.annotation_ctx.canvas_transform.canvas_height)
    if (point_is_intersecting_circle(point, polygon.points[0])) {
      this.finish_drawing_polygon(polygon, coordinator_result, annotation_event)
    }
    polygon.add_point(corrected_point)
  }

  public deselect(annotation_event: ImageInteractionEvent): void {
    let instance = this.instance
    if(annotation_event && annotation_event.annotation_ctx && annotation_event.annotation_ctx.polygon_merge_tool){
      let hover_index = annotation_event.annotation_ctx.instance_hover_index
      let hovered_instance = annotation_event.annotation_ctx.instance_list[hover_index] as PolygonInstance
      if(hovered_instance){
        instance = hovered_instance
      }
      if (instance) {
        // Allow only selection of polygon with the same label file ID.
        annotation_event.annotation_ctx.polygon_merge_tool.update_instances_to_merge(instance);
      }
    }
    instance.set_color_from_label();
    instance.unselect()

  }
  public select(annotation_event: ImageInteractionEvent): void {
    let instance = this.instance as PolygonInstance
    if(annotation_event.annotation_ctx.polygon_merge_tool){
      let hover_index = annotation_event.annotation_ctx.instance_hover_index
      let hovered_instance = annotation_event.annotation_ctx.instance_list[hover_index] as PolygonInstance
      if(hovered_instance){
        instance = hovered_instance
      }
      if (instance) {
        // Allow only selection of polygon with the same label file ID.
        annotation_event.annotation_ctx.polygon_merge_tool.update_instances_to_merge(instance);
      }
    }

    let select_color_stroke = GLOBAL_SELECTED_COLOR;
    instance.set_border_color(select_color_stroke);
    instance.set_fill_color(255, 255, 255, 0.1);
    instance.select()

  }
  public perform_action_from_event(annotation_event: ImageInteractionEvent): CoordinatorProcessResult {
    let instance = this.instance as PolygonInstance
    let result: CoordinatorProcessResult = {
      instance_moved: false,
      is_actively_drawing: annotation_event.annotation_ctx.is_actively_drawing,
      original_edit_instance: annotation_event.annotation_ctx.original_edit_instance,
      instance_hover_index: annotation_event.annotation_ctx.instance_list.indexOf(this.instance),
      instance_hover_type: this.instance ? this.instance.type : null,
      locked_editing_instance: annotation_event.annotation_ctx.locked_editing_instance,
      lock_point_hover_change: annotation_event.annotation_ctx.lock_point_hover_change,
      polygon_point_hover_index: instance ? instance.polygon_point_hover_index : null,
      auto_border_context: annotation_event.annotation_ctx.auto_border_context
    }
    // Polygon Select
    if (this.should_select_instance(annotation_event)) {
      this.select(annotation_event)
    } else if (this.should_deselect_instance(annotation_event)) {

      this.deselect(annotation_event)
    }

    // Polygon Move
    if (this.should_start_moving_polygon_points(annotation_event)) {
      this.start_polygon_point_move(result)
    } else if (this.should_move_polygon_points(annotation_event)) {
      this.move_polygon_points(result, annotation_event)
    } else if (this.should_stop_move_polygon_points(annotation_event)) {
      this.stop_polygon_move(result, annotation_event)
    }

    // Polygon Drag
    if (this.should_start_dragging_polygon(annotation_event)) {
      this.start_polygon_drag(result)
    } else if (this.should_drag_polygon(annotation_event)) {
      this.drag_polygon(result, annotation_event)
    } else if (this.should_stop_drag_polygon(annotation_event)) {
      this.stop_polygon_move(result, annotation_event)
    }

    // Polygon Drag
    if (this.should_start_dragging_polygon(annotation_event)) {
      this.start_polygon_drag(result)
    } else if (this.should_drag_polygon(annotation_event)) {
      this.drag_polygon(result, annotation_event)
    } else if (this.should_stop_drag_polygon(annotation_event)) {
      this.stop_polygon_move(result, annotation_event)
    }


    // Polygon Midpoints
    if (this.should_detect_polygon_point(annotation_event)) {
      this.detect_polygon_midpoints()
    }
    if (this.should_insert_polygon_midpoint(annotation_event)) {
      this.insert_polygon_midpoint(result, annotation_event)
    }

    // Delete
    if (this.polygon_should_delete_point(annotation_event)) {
      this.polygon_delete_point(result)
    }

    // Autoborder
    if (this.should_set_autoborder_point_index(annotation_event)) {
      this.polygon_auto_border_set_indexes(result, annotation_event)
    }
    // Start Drawing
    if (this.should_start_drawing(annotation_event)) {
      this.start_polygon_draw(result, annotation_event)
    }
    if (this.should_use_turbo_mode(annotation_event)) {
      this.add_point_turbo_mode(result, annotation_event)
    }
    if (this.should_add_polygon_point(annotation_event)) {
      this.add_polygon_point(result, annotation_event)
    }
    if (this.should_finish_polygon_draw_hotkey(annotation_event)) {
      let polygon = annotation_event.annotation_ctx.current_drawing_instance as PolygonInstance
      this.finish_drawing_polygon(polygon, result, annotation_event)
    }


    return result
  }

}
