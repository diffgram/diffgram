import {CoordinatorGenerator} from "./CoordinatorGenerator";
import {Coordinator} from "./Coordinator";
import {Instance} from "../instances/Instance";
import {KeypointInstanceCoordinator} from "./coordinator_types/keypoints/KeypointInstanceCoordinator";
import {KeypointInstance} from "../instances/KeypointInstance";


export class InstanceTemplateCoordinatorGenerator implements CoordinatorGenerator {
  instance_hover_index: number;
  instance_list: Instance[];
  current_instance: Instance;
  draw_mode: boolean;
  event: Event;
  color_tool_active: boolean

  constructor(event, instance_hover_index, instance_list, draw_mode, current_instance, color_tool_active = false) {
    this.event = event;
    this.instance_hover_index = instance_hover_index;
    this.current_instance = current_instance;
    this.instance_list = instance_list;
    this.draw_mode = draw_mode;
    this.color_tool_active = color_tool_active;

  }
  private get_hovered_instance(): Instance{
    if(!this.instance_list || this.instance_hover_index == undefined){ return undefined }
    return this.instance_list[this.instance_hover_index];
  }

  private generate_mousedown_interactions(): Coordinator{
    const instance = this.get_hovered_instance();
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceCoordinator(instance as KeypointInstance, this.draw_mode)
    }
    return undefined;
  }

  private generate_mouseup_interaction(): Coordinator{
    let instance = this.get_hovered_instance();
    let current_instance = this.current_instance;
    if(!instance){
      instance = current_instance;
    }
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceCoordinator(instance as KeypointInstance, this.draw_mode)
    }
    return undefined;
  }

  private generate_mousemove_interactions(): Coordinator{
    const instance = this.get_hovered_instance() as KeypointInstance;
    if(instance && instance.type === 'keypoints'){
      return new KeypointInstanceCoordinator(instance, this.draw_mode)
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
