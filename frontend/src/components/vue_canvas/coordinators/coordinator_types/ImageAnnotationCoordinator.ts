import {ImageAnnotationEventCtx, ImageInteractionEvent} from "../../../../types/InteractionEvent";
import {Coordinator, CoordinatorProcessResult} from "../Coordinator";
import {CanvasMouseCtx} from "../../../../types/mouse_position";
import {BoxInstance} from "../../instances/BoxInstance";
import {GLOBAL_SELECTED_COLOR, Instance} from "../../instances/Instance";

export abstract class ImageAnnotationCoordinator extends Coordinator{
  /*
  * Extends the base coordinator for the context of image annotation.
  * */
  instance: Instance
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

  public select(): void {
    let select_color_stroke = GLOBAL_SELECTED_COLOR;
    this.instance.set_border_color(select_color_stroke);
    this.instance.set_fill_color(255, 255, 255, 0.1);
    this.instance.select()

  }

  public deselect(): void {
    this.instance.set_color_from_label();
    this.instance.unselect()

  }

  public canvas_mouse_ctx: CanvasMouseCtx
}
