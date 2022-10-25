import {AnnotationToolEvent} from "../../../types/AnnotationToolEvent";

export type CoordinatorProcessResult = {
  instance_moved?: boolean
  is_actively_drawing?: boolean

}

export abstract class Coordinator {
  public type: string

  abstract perform_action_from_event(ann_tool_event: AnnotationToolEvent): CoordinatorProcessResult

}
