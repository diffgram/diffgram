import {Instance} from "../components/vue_canvas/instances/Instance";
import {LabelColourMap} from "./label_colour_map";
import {MousePosition} from "./mouse_position";
import {ImageCanvasTransform} from "./CanvasTransform";

export type AnnotationToolEvent = {
  dom_event: MouseEvent
  annotation_ctx: AnnotationEventCtx
}
export type AnnotationEventCtx = {
  label_file_id: number
  instance_type: string

}

export type ImageAnnotationToolEvent = {
  dom_event: MouseEvent
  annotation_ctx: ImageAnnotationEventCtx
}

export interface ImageAnnotationEventCtx extends AnnotationEventCtx {
  draw_mode: boolean
  hovered_instance?: Instance
  is_actively_drawing: boolean
  current_drawing_instance: Instance
  label_file_colour_map: LabelColourMap
  mouse_position: MousePosition
  canvas_transform: ImageCanvasTransform
  canvas_element: HTMLCanvasElement
  view_issue_mode: boolean

}

export const genAnnotationEvent = (dom_event: MouseEvent, annotation_ctx: AnnotationEventCtx): AnnotationToolEvent => {
  let result: AnnotationToolEvent = {
    dom_event: dom_event,
    annotation_ctx: annotation_ctx
  }
  return result
}

export const genImageAnnotationEvent = (dom_event: MouseEvent, annotation_ctx: ImageAnnotationEventCtx): AnnotationToolEvent => {
  let result: ImageAnnotationToolEvent = {
    dom_event: dom_event,
    annotation_ctx: annotation_ctx
  }
  return result
}
