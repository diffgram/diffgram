import {Coordinator, CoordinatorProcessResult} from "../Coordinator";
import {
  InteractionEvent,
  ImageAnnotationEventCtx,
  ImageInteractionEvent
} from "../../../../types/InteractionEvent";
import {ImageAnnotationCoordinator} from "./ImageAnnotationCoordinator";
import {CanvasMouseCtx, Point, point_is_intersecting_circle} from "../../../../types/mouse_position";
import CommandManager from "../../../../helpers/command/command_manager";
import {PolygonInstance, PolygonPoint} from "../../instances/PolygonInstance";
import {BoxInstance} from "../../instances/BoxInstance";

export class PolygonInstanceCoordinator extends ImageAnnotationCoordinator {
  /**
   * Routes an annotation_event and interaction of a user to box instances.
   * */
  snap_to_edges_num_pixels = 5

  constructor(box_instance, canvas_mouse_ctx: CanvasMouseCtx, command_manager: CommandManager) {
    super();
    this.instance = box_instance
    this.canvas_mouse_ctx = canvas_mouse_ctx
    this.command_manager = command_manager
  }
  private should_start_drawing(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_down_event(annotation_event) &&
      !annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
  }
  private start_polygon_draw(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent){
    this.initialize_instance_drawing(coordinator_result, annotation_event)
  }
  private should_add_polygon_point(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_up_event(annotation_event) &&
      annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
  }
  private check_point_canvas_limits(point: Point, canvas_width: number, canvas_height: number): PolygonPoint{
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
  public finish_drawing_polygon(instance: PolygonInstance, coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent){
    let polygon = annotation_event.annotation_ctx.current_drawing_instance as BoxInstance
    this.finish_drawing_instance(polygon, coordinator_result, annotation_event)

  }

  private add_polygon_point(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent){
    coordinator_result.is_actively_drawing = true
    let polygon = annotation_event.annotation_ctx.current_drawing_instance as PolygonInstance
    let point = annotation_event.annotation_ctx.mouse_position
    let corrected_point = this.check_point_canvas_limits(point,
      annotation_event.annotation_ctx.canvas_transform.canvas_width,
      annotation_event.annotation_ctx.canvas_transform.canvas_height)
    if(point_is_intersecting_circle(point, polygon.points[0])){
      this.finish_drawing_polygon(polygon, coordinator_result, annotation_event)
    }
    polygon.add_point(corrected_point)
  }

  public perform_action_from_event(annotation_event: ImageInteractionEvent): CoordinatorProcessResult {
    let result: CoordinatorProcessResult = {
      instance_moved: false,
      is_actively_drawing: annotation_event.annotation_ctx.is_actively_drawing,
      original_edit_instance: annotation_event.annotation_ctx.original_edit_instance,
      instance_hover_index: annotation_event.annotation_ctx.instance_list.indexOf(this.instance),
      instance_hover_type: this.instance ? this.instance.type : null,
      locked_editing_instance: annotation_event.annotation_ctx.locked_editing_instance,
      lock_point_hover_change: annotation_event.annotation_ctx.lock_point_hover_change,
    }
    // Polygon Select
    console.log('should_deselect_instance POLYGON', this.should_deselect_instance(annotation_event) )
    if (this.should_select_instance(annotation_event)) {
      this.select()
    }
    else if (this.should_deselect_instance(annotation_event)) {
      this.deselect()
    }

    // Start Drawing
    if(this.should_start_drawing(annotation_event)){
      this.start_polygon_draw(result, annotation_event)
    }
    if(this.should_add_polygon_point(annotation_event)){
      this.add_polygon_point(result, annotation_event)
    }

    return result
  }

}
