import {Coordinator, CoordinatorProcessResult} from "../../Coordinator";
import {BoxInstance} from "../../../instances/BoxInstance";
import {ImageAnnotationEventCtx} from "../../../../../types/AnnotationToolEvent";
import {ImageAnnotationCoordinator} from "../ImageAnnotationCoordinator";

export class BoxInstanceCoordinator extends ImageAnnotationCoordinator{
  /**
   * Routes an annotation_event and interaction of a user to box instances.
   * */
  box_instance: BoxInstance
  annotation_event: ImageAnnotationEventCtx

  constructor(box_instance, annotation_event: ImageAnnotationEventCtx) {
    super();
    this.box_instance = box_instance
    this.annotation_event = annotation_event
  }
  public process_mouse_down(): CoordinatorProcessResult {
    console.log('process_mouse_down BOX', this.box_instance)
    let result: CoordinatorProcessResult = {
      instance_moved: false
    }
    if(!this.box_instance && !this.annotation_event.is_actively_drawing){
      let currently_drawing_box: BoxInstance = this.annotation_event.current_drawing_instance as BoxInstance
      currently_drawing_box.set_actively_drawing(true)
      result.is_actively_drawing = true
    }

    return result;
  }
  public process_mouse_up(): boolean {

    return false;
  }
  public process_mouse_move(): boolean {

    return false;
  }

}
