import {Coordinator, CoordinatorProcessResult} from "../Coordinator";
import {KeypointInstance} from "../../instances/KeypointInstance";
import {iconFillPaint} from "../../../../../embed/src/types/utils/custom_icons"
import CommandManager from "../../../../../src/helpers/command/command_manager";
import {ImageAnnotationCoordinator} from "./ImageAnnotationCoordinator";
import {ImageInteractionEvent, InteractionEvent} from "../../annotation/InteractionEvent";

export class KeypointInstanceCoordinator extends ImageAnnotationCoordinator{
  /**
   * Represents the interaction of a user pressing the mouse button
   * over a keypoint instance (either over a node or over the bounding box.
   * */
  instance: KeypointInstance
  command_manager: CommandManager

  constructor(key_point_instance: KeypointInstance, draw_mode: boolean, command_manager: CommandManager) {
    super();
    this.instance = key_point_instance
    this.command_manager = command_manager
  }
  private set_hover_scale_points(): void {
    let key = this.instance.hovered_control_point_key;
    if (['top'].includes(key)) {
      this.instance.ctx.canvas.style.cursor = 'n-resize'
    } else if (['bottom'].includes(key)) {
      this.instance.ctx.canvas.style.cursor = 's-resize'
    } else if (['left'].includes(key)) {
      this.instance.ctx.canvas.style.cursor = 'w-resize'
    } else if (['right'].includes(key)) {
      this.instance.ctx.canvas.style.cursor = 'e-resize'
    } else if (['top_right'].includes(key)) {
      this.instance.ctx.canvas.style.cursor = 'ne-resize'
    } else if (['top_left'].includes(key)) {
      this.instance.ctx.canvas.style.cursor = 'nw-resize'
    } else if (['bottom_right'].includes(key)) {
      this.instance.ctx.canvas.style.cursor = 'se-resize'
    } else if (['bottom_left'].includes(key)) {
      this.instance.ctx.canvas.style.cursor = 'sw-resize'
    }
  }
  public process_mouse_up() {
    /*
    * Handles the mouse up event for the keypoint instance by adding a node
    * selecting, or finishing a drag depending on the instances's state.
    * */
    let result: CoordinatorProcessResult = {
      instance_moved: false
    }
    result.instance_moved = this.instance.process_mouse_up()
    return result
  }
  public process_mouse_down(): CoordinatorProcessResult {
    let result: CoordinatorProcessResult = {
      instance_moved: false
    }
    this.instance.start_movement()
    return result;
  }

  public process_mouse_move(event: ImageInteractionEvent) {
    let result: CoordinatorProcessResult = {
      instance_moved: false
    }
    let draw_mode = event.annotation_ctx.draw_mode
    if (draw_mode) {
      this.instance.ctx.canvas.style.cursor = 'none'
    } else {
      this.instance.ctx.canvas.style.cursor = 'default'
    }

    if (this.instance.is_node_hovered &&
      this.instance.instance_context.draw_mode &&
      !this.instance.instance_context.color_tool_active) {
      this.instance.ctx.canvas.style.cursor = 'copy'
    } else if (this.instance.instance_context.color_tool_active
      && (this.instance.is_edge_hovered || this.instance.is_node_hovered)) {
      this.instance.ctx.canvas.style.cursor = `url(${iconFillPaint}) 24 24, auto`;
    } else if (this.instance.hovered_scale_control_points) {
      this.set_hover_scale_points();
    } else if (this.instance.is_node_hovered &&
      !this.instance.instance_context.draw_mode &&
      !this.instance.instance_context.color_tool_active) {
      this.instance.ctx.canvas.style.cursor = 'pointer'
    } else if (!this.instance.instance_context.draw_mode
      && this.instance.instance_rotate_control_mouse_hover) {
      this.instance.ctx.canvas.style.cursor = 'help'
    } else if (!this.instance.is_node_hovered
      && !this.instance.instance_context.draw_mode
      && this.instance.is_bounding_box_hovered && !this.instance.template_creation_mode) {
      this.instance.ctx.canvas.style.cursor = 'move'

      if (this.instance.instance_rotate_control_mouse_hover) {
        this.instance.ctx.canvas.style.cursor = 'help'
      }
    } else if (this.instance.is_bounding_box_hovered && !this.instance.instance_context.draw_mode) {
      this.instance.ctx.canvas.style.cursor = 'all-scroll'
    }
    if (!this.instance.instance_context.draw_mode) {
      result.instance_moved = this.instance.move()
      return result;
    }
    return result
  }
  private start_moving_keypoint_instance(){
    let result: CoordinatorProcessResult = {
      instance_moved: false
    }
    this.instance.start_movement()
    return result;
  }
  private should_start_drawing_keypoints(annotation_event: ImageInteractionEvent){
    return annotation_event.annotation_ctx.draw_mode && this.is_mouse_down_event(annotation_event)
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
    if(this.is_mouse_down_event(annotation_event)){
      this.process_mouse_down()
    }

    if(this.is_mouse_up_event(annotation_event)){
      this.process_mouse_up()
    }

    if(this.is_mouse_move_event(annotation_event)){
      this.process_mouse_move(annotation_event)
    }

    return result
  }
}
