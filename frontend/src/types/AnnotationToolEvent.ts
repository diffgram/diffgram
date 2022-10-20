
export type AnnotationToolEvent = {
  dom_event: MouseEvent
  annotation_ctx: AnnotationEventCtx
}

export type AnnotationEventCtx = {
  label_file_id: number
  instance_type: string
}
export const genAnnotationEvent = (dom_event: MouseEvent, annotation_ctx: AnnotationEventCtx): AnnotationToolEvent => {
  let result: AnnotationToolEvent = {
    dom_event: dom_event,
    annotation_ctx: annotation_ctx
  }
  return result
}
