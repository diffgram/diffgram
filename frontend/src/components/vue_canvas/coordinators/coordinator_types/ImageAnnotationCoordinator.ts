import {ImageAnnotationEventCtx, ImageInteractionEvent} from "../../../../types/InteractionEvent";
import {Coordinator} from "../Coordinator";
import {CanvasMouseCtx} from "../../../../types/mouse_position";

export abstract class ImageAnnotationCoordinator extends Coordinator{
  /*
  * Extends the base coordinator for the context of image annotation.
  * */
  protected is_mouse_down_event(event: ImageInteractionEvent): boolean {
    if (event.dom_event.type === 'mousedown') {
      return true
    }
    return false
  }

  protected is_mouse_up_event(event: ImageInteractionEvent): boolean {
    if (event.dom_event.type === 'mouseup') {
      return true
    }
    return false
  }
  protected is_mouse_move_event(event: ImageInteractionEvent): boolean {
    if (event.dom_event.type === 'mousemove') {
      return true
    }
    return false
  }

  public canvas_mouse_ctx: CanvasMouseCtx
}
