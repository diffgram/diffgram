import {Interaction} from "../../Interaction";
import {KeypointInstance} from "../../../instances/KeypointInstance";

export class KeypointInstanceMouseDown extends Interaction{
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
    this.key_point_instance.start_movement()
  }

}
