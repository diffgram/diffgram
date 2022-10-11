import {Instance} from "../components/vue_canvas/instances/Instance";

export type Raw = {
  x: number
  y: number
}
export type MousePosition = {
  x: number
  y: number
  raw?: Raw
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
  label_settings: any
}
