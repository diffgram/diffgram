import {Instance} from "../components/vue_canvas/instances/Instance";
import {ImageCanvasTransform} from "./CanvasTransform";
import {createDefaultLabelSettings, ImageLabelSettings} from "./image_label_settings";


export type Point = {
  x: number
  y: number

}

export type MousePosition = {
  x: number
  y: number
  raw?: Point
}
export function point_is_intersecting_circle (mouse: MousePosition,
                                              point: Point,
                                              radius = 8,
                                              zoom_value: number = 1): boolean{
  if(!point){
    return false
  }
  if(!mouse){
    return false
  }
  let radius_scaled = radius / zoom_value;
  const result =
    Math.sqrt((point.x - mouse.x) ** 2 + (mouse.y - point.y) ** 2) <
    radius_scaled; // < number == circle.radius
  return result;
}

export type CanvasMouseCtx ={
  mouse_position: MousePosition
  canvas_element_ctx:  any
  instance_context: any
  trigger_instance_changed: () => void,
  instance_selected: () => void,
  instance_deselected: () => void,
  new_global_instance: () => Instance,
  mouse_down_delta_event: MousePosition,
  mouse_down_position: MousePosition,
  label_settings: ImageLabelSettings
  canvas_transform: ImageCanvasTransform
}
export function newEmptyCanvasMouseCtx(): CanvasMouseCtx {
  let result: CanvasMouseCtx = {
    mouse_position: {
      x: 0,
      y: 0
    },
    canvas_element_ctx: {},
    instance_context: {},
    trigger_instance_changed: () => {},
    instance_selected: () => {},
    instance_deselected: () => {},
    new_global_instance: () => {return new Instance()},
    mouse_down_delta_event: {
      x: 0,
      y: 0
    },
    mouse_down_position: {
      x: 0,
      y: 0
    },
    label_settings: createDefaultLabelSettings(),
    canvas_transform: null

  }
  return result
}
