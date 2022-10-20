import {AnnotationToolEvent} from "../../../types/AnnotationToolEvent";

export type CoordinatorProcessResult = {
  instance_moved?: boolean
  is_actively_drawing?: boolean

}

export abstract class Coordinator {
  public type: string

  abstract process_mouse_down(): CoordinatorProcessResult

  abstract process_mouse_up(): CoordinatorProcessResult

  abstract process_mouse_move(): CoordinatorProcessResult

}
