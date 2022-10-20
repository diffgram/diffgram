import {CoordinatorGenerator} from "./CoordinatorGenerator";
import {Coordinator} from "./Coordinator";
import {Instance} from "../instances/Instance";
import {KeypointInstance} from "../instances/KeypointInstance";
import {KeypointInstanceCoordinator} from "./coordinator_types/keypoints/KeypointInstanceCoordinator";
import {BoxInstance} from "../instances/BoxInstance";
import {BoxInstanceCoordinator} from "./coordinator_types/box/BoxInstanceCoordinator";
import {AnnotationToolEvent} from "../../../types/AnnotationToolEvent";

type InstanceTypes2D = 'box' | 'polygon' | 'tag' | 'point' | 'line' | 'cuboid' | 'ellipse' | 'curve'

export class ImageAnnotationCoordinatorCoreGenerator implements CoordinatorGenerator {
  instance_hover_index: number;
  instance_list: Instance[];
  draw_mode: boolean;
  event: MouseEvent;
  annotation_event: AnnotationToolEvent;
  instance_type: InstanceTypes2D;

  constructor(event: AnnotationToolEvent,
              instance_hover_index: number,
              instance_list: Instance[],
              draw_mode: boolean,
              instance_type: InstanceTypes2D) {
    this.annotation_event = event;
    this.event = this.annotation_event.dom_event;
    this.instance_hover_index = instance_hover_index;
    this.instance_list = instance_list;
    this.draw_mode = draw_mode;
    this.instance_type = instance_type;

  }
  private get_hovered_instance(): Instance{
    if(!this.instance_list || this.instance_hover_index == undefined){ return undefined }
    return this.instance_list[this.instance_hover_index];
  }

  private generate_mousedown_interactions(): Coordinator{
    const instance = this.get_hovered_instance();
    const instance_type = instance ? instance.type : this.instance_type
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceCoordinator(instance as KeypointInstance, this.draw_mode)
    }

    if(instance_type === 'box'){
      return new BoxInstanceCoordinator(instance as BoxInstance)
    }

  }

  private generate_mouseup_interaction(): Coordinator{
    const instance = this.get_hovered_instance();
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceCoordinator(instance as KeypointInstance, this.draw_mode)
    }
    return undefined;
  }

  private generate_mousemove_interactions(): Coordinator{
    const instance = this.get_hovered_instance() as KeypointInstance;
    const instance_type = instance ? instance.type : this.instance_type
    if(instance_type === 'keypoints'){
      return new KeypointInstanceCoordinator(instance as KeypointInstance, this.draw_mode)
    }

    return undefined;
  }

  generate_coordinator(): Coordinator {
    if(this.event.type === 'mousedown'){
      return this.generate_mousedown_interactions()
    }
    if(this.event.type === 'mouseup'){
      return this.generate_mouseup_interaction()
    }

    if(this.event.type === 'mousemove'){
      return this.generate_mousemove_interactions()
    }

    return undefined;
  }


}
