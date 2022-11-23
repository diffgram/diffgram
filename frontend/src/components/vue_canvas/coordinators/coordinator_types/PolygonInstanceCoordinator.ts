import {Coordinator, CoordinatorProcessResult} from "../Coordinator";
import {BoxInstance} from "../../instances/BoxInstance";
import {
  InteractionEvent,
  ImageAnnotationEventCtx,
  ImageInteractionEvent
} from "../../../../types/InteractionEvent";
import {ImageAnnotationCoordinator} from "./ImageAnnotationCoordinator";
import {duplicate_instance} from "../../../../utils/instance_utils";
import {CanvasMouseCtx, Point} from "../../../../types/mouse_position";
import {CreateInstanceCommand} from "../../../annotation/commands/create_instance_command";
import CommandManager from "../../../../helpers/command/command_manager";
import {InstanceColor} from "../../../../types/instance_color";
import {UpdateInstanceCommand} from "../../../annotation/commands/update_instance_command";
import {PolygonInstance} from "../../instances/PolygonInstance";

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
  private should_add_polygon_point(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_up_event(annotation_event) &&
      !annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
  }
  private check_point_canvas_limits(point: Point, canvas_width: number, canvas_height: number){
    let result = point
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
  private add_polygon_point(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent){
    coordinator_result.is_actively_drawing = true
    let polygon = annotation_event.annotation_ctx.current_drawing_instance as PolygonInstance
    let point = annotation_event.annotation_ctx.mouse_position
    let corrected_point = this.check_point_canvas_limits(point,
      annotation_event.annotation_ctx.canvas_transform.canvas_width,
      annotation_event.annotation_ctx.canvas_transform.canvas_height)
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
    // Start Drawing
    if(this.should_add_polygon_point(annotation_event)){
      this.add_polygon_point(result, annotation_event)
    }

    return result
  }

}
