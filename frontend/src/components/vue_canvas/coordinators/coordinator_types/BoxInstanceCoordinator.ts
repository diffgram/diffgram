import {Coordinator, CoordinatorProcessResult} from "../Coordinator";
import {BoxInstance} from "../../instances/BoxInstance";
import {
  InteractionEvent,
  ImageAnnotationEventCtx,
  ImageInteractionEvent
} from "../../../../types/InteractionEvent";
import {ImageAnnotationCoordinator} from "./ImageAnnotationCoordinator";
import {duplicate_instance} from "../../../../utils/instance_utils";
import {CanvasMouseCtx} from "../../../../types/mouse_position";
import CommandManager from "../../../../helpers/command/command_manager";
import {InstanceColor} from "../../../../types/instance_color";

export class BoxInstanceCoordinator extends ImageAnnotationCoordinator {
  /**
   * Routes an annotation_event and interaction of a user to box instances.
   * */


  constructor(box_instance, canvas_mouse_ctx: CanvasMouseCtx, command_manager: CommandManager) {
    super();
    this.instance = box_instance
    this.canvas_mouse_ctx = canvas_mouse_ctx
    this.command_manager = command_manager
  }


  public select(annotation_event) {
    super.select(annotation_event);
    let box = this.instance as BoxInstance
    box.show_box_corners()
  }

  public deselect(annotation_event: ImageInteractionEvent) {
    super.deselect(annotation_event)
    let box = this.instance as BoxInstance
    box.hide_box_corners()
  }

  private should_start_drawing_box(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_down_event(annotation_event) &&
      !annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
  }

  private should_resize_new_box(annotation_event: ImageInteractionEvent): boolean {

    return this.is_mouse_move_event(annotation_event)
      && annotation_event.annotation_ctx.current_drawing_instance
      && annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
  }

  private save_original_instance_for_undo(): BoxInstance {

    let box = this.instance as BoxInstance
    const original_edit_instance = box.duplicate_for_undo()
    return original_edit_instance
  }

  private start_drawing_box(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent): void {
    this.initialize_instance_drawing(coordinator_result, annotation_event)
  }

  private do_new_box_resize(annotation_event: ImageInteractionEvent) {
    let box_instance = annotation_event.annotation_ctx.current_drawing_instance as BoxInstance
    if (annotation_event.annotation_ctx.view_issue_mode) {
      // When viewing an issue we will not allow moving/resizing of instances
      box_instance.set_mouse_cursor_from_hovered_point('blocked')
      return
    }

    box_instance.resize_from_mouse_position(
      annotation_event.dom_event,
      annotation_event.annotation_ctx.mouse_position,
      annotation_event.annotation_ctx.mouse_down_position,
    )
  }

  private should_finish_box_drawing(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_down_event(annotation_event) &&
      annotation_event.annotation_ctx.current_drawing_instance &&
      annotation_event.annotation_ctx.draw_mode &&
      annotation_event.annotation_ctx.current_drawing_instance.width > 0 &&
      annotation_event.annotation_ctx.current_drawing_instance.height > 0 &&
      annotation_event.annotation_ctx.is_actively_drawing
  }

  private finish_box_drawing(result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent): void {
    let box = annotation_event.annotation_ctx.current_drawing_instance as BoxInstance
    this.finish_drawing_instance(box, result, annotation_event)

  }
  private should_start_moving_box(annotation_event: ImageInteractionEvent): boolean {

    let box = this.instance as BoxInstance
    return this.is_mouse_down_event(annotation_event) &&
      box &&
      box.is_hovered &&
      !box.soft_delete &&
      box.box_edit_point_hover == 'not_intersecting_special_points' &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private should_stop_moving_box(annotation_event: ImageInteractionEvent): boolean {
    let box = annotation_event.annotation_ctx.locked_editing_instance as BoxInstance
    return this.is_mouse_up_event(annotation_event) &&
      box &&
      box.selected &&
      box.is_moving &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private should_drag_box(annotation_event: ImageInteractionEvent): boolean {
    let box = annotation_event.annotation_ctx.locked_editing_instance as BoxInstance

    return this.is_mouse_move_event(annotation_event) &&
      box &&
      box.selected &&
      !box.soft_delete &&
      box.is_moving &&
      !box.is_resizing &&
      box.box_edit_point_hover == 'not_intersecting_special_points' &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private should_start_resizing_box(annotation_event: ImageInteractionEvent): boolean {
    let box = this.instance as BoxInstance
    return this.is_mouse_down_event(annotation_event) &&
      box &&
      box.selected &&
      !box.soft_delete &&
      (box.box_edit_point_hover == 'x_min_y_min' ||
        box.box_edit_point_hover == 'x_max_y_min' ||
        box.box_edit_point_hover == 'x_min_y_max' ||
        box.box_edit_point_hover == 'x_max_y_max') &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }
  private should_stop_resizing_box(annotation_event: ImageInteractionEvent): boolean {
    let box = annotation_event.annotation_ctx.locked_editing_instance as BoxInstance
    return this.is_mouse_up_event(annotation_event) &&
      box &&
      box.selected &&
      box.is_resizing &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private should_resize_box(annotation_event: ImageInteractionEvent): boolean {
    let box = annotation_event.annotation_ctx.locked_editing_instance as BoxInstance
    return this.is_mouse_move_event(annotation_event) &&
      box &&
      box.selected &&
      !box.is_moving &&
      box.is_resizing &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private start_box_move(result: CoordinatorProcessResult) {
    let box = this.instance as BoxInstance
    let original_instance = this.save_original_instance_for_undo()

    box.set_is_moving(true)
    result.locked_editing_instance = box
    result.original_edit_instance = original_instance

  }

  private do_box_drag(result: CoordinatorProcessResult) {
    let box = this.instance as BoxInstance
    box.move_from_mouse_position(this.canvas_mouse_ctx.mouse_down_delta_event)
    result.instance_moved = true
    result.locked_editing_instance = box
  }

  private start_box_resize(result: CoordinatorProcessResult){

    let box = this.instance as BoxInstance
    let original_instance = this.save_original_instance_for_undo()
    box.set_is_resizing(true)
    result.lock_point_hover_change = true
    result.original_edit_instance = original_instance
    result.locked_editing_instance = box
  }

  private stop_box_resize(annotation_event: ImageInteractionEvent, result: CoordinatorProcessResult){
    let box = result.locked_editing_instance as BoxInstance
    box.set_is_resizing(false)
    this.edit_instance_command_creation(annotation_event, result)
    result.locked_editing_instance = undefined
    result.lock_point_hover_change = false

  }
  private do_box_resize(annotation_event: ImageInteractionEvent, result: CoordinatorProcessResult){
    let box = result.locked_editing_instance as BoxInstance
    box.resize_from_corner_drag(annotation_event.annotation_ctx.mouse_position)
    result.instance_moved = true
    result.locked_editing_instance = box
  }

  private stop_box_move(annotation_event: ImageInteractionEvent, result: CoordinatorProcessResult) {

    let box = result.locked_editing_instance as BoxInstance
    box.set_is_moving(false)
    this.edit_instance_command_creation(annotation_event, result)
    result.locked_editing_instance = undefined

  }

  public route_event_to_box_drawing(annotation_event: ImageInteractionEvent, result: CoordinatorProcessResult){
    // Box Drawing
    if (this.should_start_drawing_box(annotation_event)) {
      this.start_drawing_box(result, annotation_event)
    }

    else if (this.should_resize_new_box(annotation_event)) {
      this.do_new_box_resize(annotation_event)
    }
    else if (this.should_finish_box_drawing(annotation_event)) {
      this.finish_box_drawing(result, annotation_event)
    }
  }
  public perform_action_from_event(annotation_event: ImageInteractionEvent): CoordinatorProcessResult {
    let result: CoordinatorProcessResult = {
      instance_moved: false,
      is_actively_drawing: annotation_event.annotation_ctx.is_actively_drawing,
      original_edit_instance: annotation_event.annotation_ctx.original_edit_instance,
      instance_hover_index: annotation_event.annotation_ctx.instance_list.indexOf(this.instance),
      instance_hover_type: this.instance ? this.instance.type : undefined,
      locked_editing_instance: annotation_event.annotation_ctx.locked_editing_instance,
      lock_point_hover_change: annotation_event.annotation_ctx.lock_point_hover_change,
    }

    this.route_event_to_box_drawing(annotation_event, result)

    // Box Select

    if (this.should_select_instance(annotation_event)) {
      this.select(annotation_event)
    }

    else if (this.should_deselect_instance(annotation_event)) {
      this.deselect(annotation_event)
    }

    // Box Drag
    if (this.should_start_moving_box(annotation_event)) {
      this.start_box_move(result)
    }
    else if (this.should_drag_box(annotation_event)) {
      this.do_box_drag(result)
    }
    else if (this.should_stop_moving_box(annotation_event)) {
      this.stop_box_move(annotation_event, result)
    }

    // Box Resize
    else if (this.should_start_resizing_box(annotation_event)) {
      this.start_box_resize(result)
    }
    else if (this.should_stop_resizing_box(annotation_event)) {
      this.stop_box_resize(annotation_event, result)
    }
    else if(this.should_resize_box(annotation_event)){
      this.do_box_resize(annotation_event, result)
    }

    return result
  }

}
