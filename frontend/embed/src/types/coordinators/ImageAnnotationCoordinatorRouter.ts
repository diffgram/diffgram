import {CoordinatorGenerator} from "./CoordinatorGenerator";
import {Coordinator} from "./Coordinator";
import {Instance} from "../instances/Instance";
import {KeypointInstance} from "../instances/KeypointInstance";
import {KeypointInstanceCoordinator} from "./coordinator_types/KeypointInstanceCoordinator";
import {BoxInstance} from "../instances/BoxInstance";
import {BoxInstanceCoordinator} from "./coordinator_types/BoxInstanceCoordinator";
import {
  InteractionEvent,
  ImageAnnotationEventCtx,
  ImageInteractionEvent
} from "../annotation/InteractionEvent";
import {CanvasMouseCtx} from "../annotation/image/MousePosition";
import CommandManager from "../../../../src/helpers/command/command_manager";
import {ImageAnnotationCoordinator} from "./coordinator_types/ImageAnnotationCoordinator";
import {PolygonInstanceCoordinator} from "./coordinator_types/PolygonInstanceCoordinator";

type InstanceTypes2D = 'box' | 'polygon' | 'tag' | 'point' | 'line' | 'cuboid' | 'ellipse' | 'curve'

export class ImageAnnotationCoordinatorRouter implements CoordinatorGenerator {
  instance_hover_index: number;
  instance_list: Instance[];
  draw_mode: boolean;
  event: MouseEvent;
  annotation_event: ImageInteractionEvent;
  instance_type: InstanceTypes2D;
  canvas_mouse_ctx: CanvasMouseCtx;
  command_manager: CommandManager;

  constructor(annotation_event: ImageInteractionEvent,
              instance_hover_index: number,
              instance_list: Instance[],
              draw_mode: boolean,
              instance_type: InstanceTypes2D,
              canvas_mouse_ctx: CanvasMouseCtx,
              command_manager: CommandManager
  ) {
    this.annotation_event = annotation_event;
    if (this.annotation_event) {
      this.event = this.annotation_event.dom_event;
    }
    this.instance_hover_index = instance_hover_index;
    this.instance_list = instance_list;
    this.draw_mode = draw_mode;
    this.instance_type = instance_type;
    this.canvas_mouse_ctx = canvas_mouse_ctx;
    this.command_manager = command_manager;

  }

  private get_hovered_instances(): Instance[] {
    if (!this.instance_list) {
      return []
    }
    let result = []
    if(this.instance_hover_index != undefined){
      result.push(this.instance_list[this.instance_hover_index])
    }
    for (let i = 0; i < this.instance_list.length; i++) {
      if (!this.instance_list[i].soft_delete && this.instance_list[i].is_hovered && !result.includes(this.instance_list[i])) {
        result.push(this.instance_list[i])
      }
    }
    // Sort by selected instances first
    result = result.sort((a,b) => b.selected - a.selected)
    return result
  }

  private get_locked_editing_instance() {
    return this.annotation_event.annotation_ctx.locked_editing_instance
  }

  private get_selected_instance(): Instance {
    let instance = this.instance_list.filter(elm => elm.selected === true && !elm.soft_delete)
    return instance[0]
  }

  public generate_from_instance(instance: Instance, type: string): ImageAnnotationCoordinator {
    if (instance && type === 'keypoints') {
      return new KeypointInstanceCoordinator(instance as KeypointInstance, this.draw_mode, this.command_manager) as ImageAnnotationCoordinator
    }

    else if (type === 'box') {
      return new BoxInstanceCoordinator(instance as BoxInstance, this.canvas_mouse_ctx, this.command_manager)
    }
    else if (type === 'polygon') {
      return new PolygonInstanceCoordinator(instance as BoxInstance, this.canvas_mouse_ctx, this.command_manager)
    }
  }

  private get_hovered_priority(): Instance{
    if(this.annotation_event.annotation_ctx.draw_mode && this.annotation_event.annotation_ctx.current_drawing_instance){
      return this.annotation_event.annotation_ctx.current_drawing_instance
    }
    const instance_list_hovered = this.get_hovered_instances();
    const instance_hovered = instance_list_hovered[0]
    const instance_selected = this.get_selected_instance();
    const editing_instance = this.get_locked_editing_instance()
    let instance = null

    if (editing_instance) {
      instance = editing_instance
    } else if (instance_hovered) {
      instance = instance_hovered
    } else if (instance_selected) {
      instance = instance_selected
    }
    return instance
  }
  generate_coordinator(): ImageAnnotationCoordinator {
    const instance = this.get_hovered_priority()
    let instance_type = null
    if(instance){
      instance_type = instance.type
    }
    else{
      instance_type = this.instance_type
    }

    return this.generate_from_instance(instance, instance_type)


    return undefined;
  }


}
