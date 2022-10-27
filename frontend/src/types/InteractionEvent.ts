import {Instance} from "../components/vue_canvas/instances/Instance";
import {LabelColourMap} from "./label_colour_map";
import {MousePosition} from "./mouse_position";
import {ImageCanvasTransform} from "./CanvasTransform";
import {LabelFile} from "./label";

export type InteractionEvent = {
  dom_event: MouseEvent
  annotation_ctx: AnnotationEventCtx
}
export type AnnotationEventCtx = {
  label_file: LabelFile
  instance_type: string
  instance_list: Instance[]

}

export type ImageInteractionEvent = {
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
  mouse_down_position: MousePosition
  canvas_transform: ImageCanvasTransform
  canvas_element: HTMLCanvasElement
  view_issue_mode: boolean
  instance_select_for_issue: boolean
  frame_number: number
  ann_core_ctx: any
  view_only_mode: boolean

}
export interface AudioAnnotationEvent extends AnnotationEventCtx{

}

export const genAnnotationEvent = (dom_event: MouseEvent, annotation_ctx: AnnotationEventCtx): InteractionEvent => {
  let result: InteractionEvent = {
    dom_event: dom_event,
    annotation_ctx: annotation_ctx
  }
  return result
}

export const genImageAnnotationEvent = (dom_event: MouseEvent, annotation_ctx: ImageAnnotationEventCtx): InteractionEvent => {
  let result: ImageInteractionEvent = {
    dom_event: dom_event,
    annotation_ctx: annotation_ctx
  }
  return result
}
