import {CoordinatorGenerator} from "./CoordinatorGenerator";
import {Coordinator} from "./Coordinator";
import {Instance} from "../instances/Instance";
import {KeypointInstance} from "../instances/KeypointInstance";
import {KeypointInstanceCoordinator} from "./coordinator_types/keypoints/KeypointInstanceCoordinator";
import {BoxInstance} from "../instances/BoxInstance";
import {BoxInstanceCoordinator} from "./coordinator_types/box/BoxInstanceCoordinator";
import {
  AnnotationToolEvent,
  ImageAnnotationEventCtx,
  ImageAnnotationToolEvent
} from "../../../types/AnnotationToolEvent";
import {CanvasMouseCtx} from "../../../types/mouse_position";

type InstanceTypes2D = 'box' | 'polygon' | 'tag' | 'point' | 'line' | 'cuboid' | 'ellipse' | 'curve'

export class ImageAnnotationCoordinatorRouter implements CoordinatorGenerator {
  instance_hover_index: number;
  instance_list: Instance[];
  draw_mode: boolean;
  event: MouseEvent;
  annotation_event: ImageAnnotationToolEvent;
  instance_type: InstanceTypes2D;
  canvas_mouse_ctx: CanvasMouseCtx;

  constructor(annotation_event: ImageAnnotationToolEvent,
              instance_hover_index: number,
              instance_list: Instance[],
              draw_mode: boolean,
              instance_type: InstanceTypes2D,
              canvas_mouse_ctx: CanvasMouseCtx,
              ) {
    this.annotation_event = annotation_event;
    this.event = this.annotation_event.dom_event;
    this.instance_hover_index = instance_hover_index;
    this.instance_list = instance_list;
    this.draw_mode = draw_mode;
    this.instance_type = instance_type;
    this.canvas_mouse_ctx = canvas_mouse_ctx;

  }
  private get_hovered_instance(): Instance{
    if(!this.instance_list || this.instance_hover_index == undefined){ return undefined }
    return this.instance_list[this.instance_hover_index];
  }

  generate_coordinator(): Coordinator {
    const instance = this.get_hovered_instance();
    const instance_type = instance ? instance.type : this.instance_type
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceCoordinator(instance as KeypointInstance, this.draw_mode)
    }

    if(instance_type === 'box'){
      return new BoxInstanceCoordinator(instance as BoxInstance, this.canvas_mouse_ctx)
    }

    return undefined;
  }


}
