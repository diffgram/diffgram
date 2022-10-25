import {ImageAnnotationEventCtx} from "../../../../types/AnnotationToolEvent";
import {Coordinator} from "../Coordinator";
import {CanvasMouseCtx} from "../../../../types/mouse_position";

export abstract class ImageAnnotationCoordinator extends Coordinator{
  /*
  * Extends the base coordinator for the context of image annotation.
  * */
  public annotation_event: ImageAnnotationEventCtx
  public canvas_mouse_ctx: CanvasMouseCtx
}
