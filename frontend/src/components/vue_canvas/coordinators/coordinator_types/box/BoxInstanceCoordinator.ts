import {Coordinator} from "../../Coordinator";
import {BoxInstance} from "../../../instances/BoxInstance";

export class BoxInstanceCoordinator extends Coordinator{
  /**
   * Represents the interaction of a user pressing the mouse button
   * over a box instance.
   * */
  box_instance: BoxInstance

  constructor(box_instance) {
    super();
    this.box_instance = box_instance
  }
  public process_mouse_down(): boolean {

    return false;
  }
  public process_mouse_up(): boolean {

    return false;
  }
  public process_mouse_move(): boolean {

    return false;
  }

}
