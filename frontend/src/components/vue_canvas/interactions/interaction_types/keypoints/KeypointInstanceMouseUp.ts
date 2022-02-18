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
  process(): boolean {
    /*
    * Handles the mouse up event for the keypoint instance by adding a node
    * selecting, or finishing a drag depending on the instances's state.
    * */
    return this.key_point_instance.process_mouse_up()
  }

}
