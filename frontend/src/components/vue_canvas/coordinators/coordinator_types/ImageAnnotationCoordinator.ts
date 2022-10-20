import {ImageAnnotationEventCtx} from "../../../../types/AnnotationToolEvent";
import {Coordinator} from "../Coordinator";

export abstract class ImageAnnotationCoordinator extends Coordinator{
  /*
  * Extends the base coordinator for the context of image annotation.
  * */
  public annotation_event: ImageAnnotationEventCtx
}
