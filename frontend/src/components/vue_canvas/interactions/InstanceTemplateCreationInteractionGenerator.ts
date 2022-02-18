import {InteractionGenerator} from "./InteractionGenerator";
import {Interaction} from "./Interaction";
import {Instance} from "../instances/Instance";
import {KeypointInstanceMouseDown} from "./interaction_types/keypoints/KeypointInstanceMouseDown";
import {KeypointInstanceMouseMove} from "./interaction_types/keypoints/KeypointInstanceMouseMove";
import {KeypointInstanceMouseUp} from "./interaction_types/keypoints/KeypointInstanceMouseUp";
import {KeypointInstance} from "../instances/KeypointInstance";


export class InstanceTemplateCreationInteractionGenerator implements InteractionGenerator {
  instance_hover_index: number;
  instance_list: Instance[];
  current_instance: Instance;
  draw_mode: boolean;
  event: Event;

  constructor(event, instance_hover_index, instance_list, draw_mode, current_instance) {
    this.event = event;
    this.instance_hover_index = instance_hover_index;
    this.current_instance = current_instance;
    this.instance_list = instance_list;
    this.draw_mode = draw_mode;

  }
  private get_hovered_instance(): Instance{
    if(!this.instance_list || this.instance_hover_index == undefined){ return undefined }
    return this.instance_list[this.instance_hover_index];
  }

  private generate_mousedown_interactions(): Interaction{
    const instance = this.get_hovered_instance();
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceMouseDown(instance)
    }
    return undefined;
  }

  private generate_mouseup_interaction(): Interaction{
    let instance = this.get_hovered_instance();
    let current_instance = this.current_instance;
    if(!instance){
      instance = current_instance;
    }
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceMouseUp(instance)
    }
    return undefined;
  }

  private generate_mousemove_interactions(): Interaction{
    const instance = this.get_hovered_instance() as KeypointInstance;
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceMouseMove(instance, this.draw_mode)
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
