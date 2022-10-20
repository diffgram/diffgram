import {Instance} from "../components/vue_canvas/instances/Instance";

export type AnnotationToolEvent = {
  dom_event: MouseEvent
  annotation_ctx: AnnotationEventCtx
}

export type AnnotationEventCtx = {
  label_file_id: number
  instance_type: string

}
export interface ImageAnnotationEventCtx extends AnnotationEventCtx{
  draw_mode: boolean
  hovered_instance?: Instance
  is_actively_drawing: boolean
  current_drawing_instance: Instance

}
export const genAnnotationEvent = (dom_event: MouseEvent, annotation_ctx: AnnotationEventCtx): AnnotationToolEvent => {
  let result: AnnotationToolEvent = {
    dom_event: dom_event,
    annotation_ctx: annotation_ctx
  }
  return result
}
