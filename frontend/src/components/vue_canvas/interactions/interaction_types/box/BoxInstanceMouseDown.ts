import {Interaction} from "../../Interaction";
import {KeypointInstance} from "../../../instances/KeypointInstance";

export class BoxInstanceMouseDown extends Interaction{
  /**
   * Represents the interaction of a user pressing the mouse button
   * over a box instance.
   * */
  box_instance: BoxInstanceMouseDown

  constructor(box_instance) {
    super();
    this.box_instance = box_instance
  }
  process(): boolean {

    return false;
  }

}
