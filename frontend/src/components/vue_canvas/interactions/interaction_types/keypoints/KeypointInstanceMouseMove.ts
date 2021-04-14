import {Interaction} from "../../Interaction";
import {KeypointInstance} from "../../../instances/KeypointInstance";

export class KeypointInstanceMouseMove extends Interaction {
  /**
   * Represents the interaction of a user pressing the mouse button
   * over a keypoint instance (either over a node or over the bounding box.
   * */
  key_point_instance: KeypointInstance

  constructor(key_point_instance) {
    super();
    this.key_point_instance = key_point_instance
  }

  process(): void {
    this.key_point_instance.ctx.canvas.style.cursor = 'default'
    if (this.key_point_instance.is_node_hovered && this.key_point_instance.instance_context.draw_mode) {
      this.key_point_instance.ctx.canvas.style.cursor = 'copy'
    } else if (this.key_point_instance.is_node_hovered && !this.key_point_instance.instance_context.draw_mode) {
      this.key_point_instance.ctx.canvas.style.cursor = 'all-scroll'
    }
    else if (this.key_point_instance.is_bounding_box_hovered && !this.key_point_instance.instance_context.draw_mode) {
      this.key_point_instance.ctx.canvas.style.cursor = 'all-scroll'
    }

    if (!this.key_point_instance.instance_context.draw_mode) {
      this.key_point_instance.move();
    }
  }

}
