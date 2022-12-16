import {Instance} from "../instances/Instance";
import {LabelColourMap} from "../labels/LabelColourMap";
import {MousePosition} from "./image/MousePosition";
import {ImageCanvasTransform} from "./image/CanvasTransform";
import {LabelFile} from "../labels/Label";
import {ImageLabelSettings} from "./image/ImageLabelSettings";
import {Sequence} from "../annotation/image/Sequence";
import {CanvasMouseTools} from "../annotation/image/CanvasMouseTools";
import {PolygonPoint} from "../instances/PolygonInstance";
import {AutoBorderContext} from "./image/advanced_tools/PolygonAutoBorderTool";
import {PolygonMergeTool} from  "./image/advanced_tools/PolygonMergeTool";

export interface InteractionEvent {
  dom_event: Event
  annotation_ctx: AnnotationEventCtx
}

export type AnnotationEventCtx = {
  label_file: LabelFile
  instance_type: string
  instance_list: Instance[]
}

export interface ImageInteractionEvent extends InteractionEvent {
  dom_event: MouseEvent | KeyboardEvent
  annotation_ctx: ImageAnnotationEventCtx
}

export interface ImageAnnotationEventCtx extends AnnotationEventCtx {
  draw_mode: boolean
  hovered_instance?: Instance
  is_actively_drawing: boolean
  instance_hover_index: number
  lock_point_hover_change: boolean
  shift_key: boolean
  current_drawing_instance: Instance
  polygon_point_click_index: number
  polygon_point_hover_index: number
  original_edit_instance: Instance
  locked_editing_instance: Instance
  label_file_colour_map: LabelColourMap
  mouse_position: MousePosition
  mouse_down_position: MousePosition
  mouse_down_delta_event: MousePosition
  canvas_transform: ImageCanvasTransform
  canvas_mouse_tools: CanvasMouseTools
  canvas_element: HTMLCanvasElement
  image_label_settings: ImageLabelSettings
  view_issue_mode: boolean
  instance_select_for_issue: boolean
  current_sequence_from_sequence_component: Sequence
  frame_number: number
  ann_core_ctx: any
  view_only_mode: boolean
  video_mode: boolean
  auto_border_context: AutoBorderContext
  polygon_merge_tool: PolygonMergeTool

}
export interface AudioAnnotationEvent extends AnnotationEventCtx{

}

export const genAnnotationEvent = (dom_event: Event, annotation_ctx: AnnotationEventCtx): InteractionEvent => {
  let result: InteractionEvent = {
    dom_event: dom_event,
    annotation_ctx: annotation_ctx
  }
  return result
}

export const genImageAnnotationEvent = (dom_event: MouseEvent | KeyboardEvent, annotation_ctx: ImageAnnotationEventCtx): ImageInteractionEvent => {
  let result: ImageInteractionEvent = {
    dom_event: dom_event,
    annotation_ctx: annotation_ctx
  }
  return result
}
