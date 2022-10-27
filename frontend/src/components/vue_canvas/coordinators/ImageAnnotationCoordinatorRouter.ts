import {CoordinatorGenerator} from "./CoordinatorGenerator";
import {Coordinator} from "./Coordinator";
import {Instance} from "../instances/Instance";
import {KeypointInstance} from "../instances/KeypointInstance";
import {KeypointInstanceCoordinator} from "./coordinator_types/keypoints/KeypointInstanceCoordinator";
import {BoxInstance} from "../instances/BoxInstance";
import {BoxInstanceCoordinator} from "./coordinator_types/box/BoxInstanceCoordinator";
import {
  InteractionEvent,
  ImageAnnotationEventCtx,
  ImageInteractionEvent
} from "../../../types/InteractionEvent";
import {CanvasMouseCtx} from "../../../types/mouse_position";
import CommandManager from "../../../helpers/command/command_manager";

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
    this.event = this.annotation_event.dom_event;
    this.instance_hover_index = instance_hover_index;
    this.instance_list = instance_list;
    this.draw_mode = draw_mode;
    this.instance_type = instance_type;
    this.canvas_mouse_ctx = canvas_mouse_ctx;
    this.command_manager = command_manager;

  }
  private get_hovered_instance(): Instance{
    if(!this.instance_list || this.instance_hover_index == undefined){ return undefined }
    return this.instance_list[this.instance_hover_index];
  }

  generate_coordinator(): Coordinator {
    const instance = this.get_hovered_instance();
    const instance_type = instance ? instance.type : this.instance_type
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceCoordinator(instance as KeypointInstance, this.draw_mode, this.command_manager)
    }

    if(instance_type === 'box'){
      return new BoxInstanceCoordinator(instance as BoxInstance, this.canvas_mouse_ctx, this.command_manager)
    }

    return undefined;
  }


}
