import {Coordinator, CoordinatorProcessResult} from "../../Coordinator";
import {KeypointInstance} from "../../../instances/KeypointInstance";
import {iconFillPaint} from '../../../../../utils/custom_icons'
import CommandManager from "../../../../../helpers/command/command_manager";
import {ImageAnnotationCoordinator} from "../ImageAnnotationCoordinator";

export class KeypointInstanceCoordinator extends ImageAnnotationCoordinator{
  /**
   * Represents the interaction of a user pressing the mouse button
   * over a keypoint instance (either over a node or over the bounding box.
   * */
  key_point_instance: KeypointInstance
  command_manager: CommandManager
  draw_mode: boolean

  constructor(key_point_instance: KeypointInstance, draw_mode: boolean, command_manager: CommandManager) {
    super();
    this.key_point_instance = key_point_instance
    this.draw_mode = draw_mode
    this.command_manager = command_manager
  }
  private set_hover_scale_points(): void {
    // if(!this.key_point_instance.hovered_control_point_key){
    //   return
    // }
    let key = this.key_point_instance.hovered_control_point_key;
    if (['top'].includes(key)) {
      this.key_point_instance.ctx.canvas.style.cursor = 'n-resize'
    } else if (['bottom'].includes(key)) {
      this.key_point_instance.ctx.canvas.style.cursor = 's-resize'
    } else if (['left'].includes(key)) {
      this.key_point_instance.ctx.canvas.style.cursor = 'w-resize'
    } else if (['right'].includes(key)) {
      this.key_point_instance.ctx.canvas.style.cursor = 'e-resize'
    } else if (['top_right'].includes(key)) {
      this.key_point_instance.ctx.canvas.style.cursor = 'ne-resize'
    } else if (['top_left'].includes(key)) {
      this.key_point_instance.ctx.canvas.style.cursor = 'nw-resize'
    } else if (['bottom_right'].includes(key)) {
      this.key_point_instance.ctx.canvas.style.cursor = 'se-resize'
    } else if (['bottom_left'].includes(key)) {
      this.key_point_instance.ctx.canvas.style.cursor = 'sw-resize'
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
    result.instance_moved = this.key_point_instance.process_mouse_up()
    return result
  }
  public process_mouse_down(): CoordinatorProcessResult {
    let result: CoordinatorProcessResult = {
      instance_moved: false
    }
    this.key_point_instance.start_movement()
    return result;
  }

  public process_mouse_move() {
    let result: CoordinatorProcessResult = {
      instance_moved: false
    }
    if (this.draw_mode && !this.key_point_instance.instance_context.color_tool_active) {
      this.key_point_instance.ctx.canvas.style.cursor = 'none'
    } else {
      this.key_point_instance.ctx.canvas.style.cursor = 'default'
    }

    if (this.key_point_instance.is_node_hovered &&
      this.key_point_instance.instance_context.draw_mode &&
      !this.key_point_instance.instance_context.color_tool_active) {
      this.key_point_instance.ctx.canvas.style.cursor = 'copy'
    } else if (this.key_point_instance.instance_context.color_tool_active
      && (this.key_point_instance.is_edge_hovered || this.key_point_instance.is_node_hovered)) {
      this.key_point_instance.ctx.canvas.style.cursor = `url(${iconFillPaint}) 24 24, auto`;
    } else if (this.key_point_instance.hovered_scale_control_points) {
      this.set_hover_scale_points();
    } else if (this.key_point_instance.is_node_hovered &&
      !this.key_point_instance.instance_context.draw_mode &&
      !this.key_point_instance.instance_context.color_tool_active) {
      this.key_point_instance.ctx.canvas.style.cursor = 'pointer'
    } else if (!this.key_point_instance.instance_context.draw_mode
      && this.key_point_instance.instance_rotate_control_mouse_hover) {
      this.key_point_instance.ctx.canvas.style.cursor = 'help'
    } else if (!this.key_point_instance.is_node_hovered
      && !this.key_point_instance.instance_context.draw_mode
      && this.key_point_instance.is_bounding_box_hovered && !this.key_point_instance.template_creation_mode) {
      this.key_point_instance.ctx.canvas.style.cursor = 'move'

      if (this.key_point_instance.instance_rotate_control_mouse_hover) {
        this.key_point_instance.ctx.canvas.style.cursor = 'help'
      }
    } else if (this.key_point_instance.is_bounding_box_hovered && !this.key_point_instance.instance_context.draw_mode) {
      this.key_point_instance.ctx.canvas.style.cursor = 'all-scroll'
    }
    if (!this.key_point_instance.instance_context.draw_mode) {
      result.instance_moved = this.key_point_instance.move()
      return result;
    }

    return result
  }
}
