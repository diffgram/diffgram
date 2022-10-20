import {InteractionGenerator} from "./InteractionGenerator";
import {Interaction} from "./Interaction";
import {Instance} from "../instances/Instance";
import {KeypointInstance} from "../instances/KeypointInstance";
import {KeypointInstanceMouseDown} from "./interaction_types/keypoints/KeypointInstanceMouseDown";
import {KeypointInstanceMouseMove} from "./interaction_types/keypoints/KeypointInstanceMouseMove";
import {KeypointInstanceMouseUp} from "./interaction_types/keypoints/KeypointInstanceMouseUp";

type InstanceTypes2D = 'box' | 'polygon' | 'tag' | 'point' | 'line' | 'cuboid' | 'ellipse' | 'curve'

export class AnnotationCoreActionCoordinator implements InteractionGenerator {
  instance_hover_index: number;
  instance_list: Instance[];
  draw_mode: boolean;
  event: Event;
  instance_type: InstanceTypes2D;

  constructor(event: Event,
              instance_hover_index: number,
              instance_list: Instance[],
              draw_mode: boolean,
              instance_type: InstanceTypes2D) {
    this.event = event;
    this.instance_hover_index = instance_hover_index;
    this.instance_list = instance_list;
    this.draw_mode = draw_mode;
    this.instance_type = instance_type;

  }
  private get_hovered_instance(): Instance{
    if(!this.instance_list || this.instance_hover_index == undefined){ return undefined }
    return this.instance_list[this.instance_hover_index];
  }

  private generate_mousedown_interactions(): Interaction{
    const instance = this.get_hovered_instance();
    const instance_type = instance ? instance.type : this.instance_type
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceMouseDown(instance)
    }

    if(instance_type === 'box'){
      return new KeypointInstanceMouseMove(instance)
    }

  }

  private generate_mouseup_interaction(): Interaction{
    const instance = this.get_hovered_instance();
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceMouseUp(instance)
    }
    return undefined;
  }

  private generate_mousemove_interactions(): Interaction{
    const instance = this.get_hovered_instance() as KeypointInstance;
    const instance_type = instance ? instance.type : this.instance_type
    if(instance_type === 'keypoints'){
      return new KeypointInstanceMouseMove(instance)
    }

    return undefined;
  }

  generate_interaction(): Interaction {
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
