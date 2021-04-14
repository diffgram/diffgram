import {Interaction} from "../../Interaction";
import {KeypointInstance} from "../../../instances/KeypointInstance";

export class KeypointInstanceMouseUp extends Interaction{
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
    /*
    * Handles the mouse up event for the keypoint instance by adding a node
    * selecting, or finishing a drag depending on the instances's state.
    * */
    if (this.key_point_instance.instance_context.draw_mode
      && this.key_point_instance.template_creation_mode) {
      this.key_point_instance.add_node_to_instance();
    } else {
      if(this.key_point_instance.is_moving){
        this.key_point_instance.stop_moving();
      }

      if(this.key_point_instance.node_hover_index != undefined){
        this.key_point_instance.select();
      }

      if(this.key_point_instance.is_dragging_instance){
        this.key_point_instance.stop_dragging()
      }

    }

  }

}
