import {BaseActionCustomButton} from "./BaseActionCustomButton";
import {ActionSetAttributeValue} from "./button_actions/ActionSetAttributeValue";
import {ActionCompleteTask} from "./button_actions/ActionCompleteTask";
import {BaseAnnotationUIContext} from "../AnnotationUIContext";

import Vue, { VueConstructor } from "vue";

export interface AnnotationUIFactory extends Vue {
  on_task_annotation_complete_and_save: () => Promise<void>;
}
export const CUSTOM_BUTTON_ACTION_TYPE = {
  set_attribute: 'set_attribute',
  complete_task: 'complete_task',
}
const action_types_map = {
  [CUSTOM_BUTTON_ACTION_TYPE.set_attribute]: ActionSetAttributeValue,
  [CUSTOM_BUTTON_ACTION_TYPE.complete_task]: ActionCompleteTask,
}

export function get_initialized_action_from_obj(action: any): BaseActionCustomButton{
  let ActionClass = action_types_map[action.type]
  if(!ActionClass){
    ActionClass = BaseActionCustomButton
  }
  const initialized_action = new ActionClass({
    metadata: action.metadata,
    type: action.type,
    name: action.name,
    workflow: this,
    id: action.id
  })
  return initialized_action
}
export class CustomButtonWorkflow {
  private actions: BaseActionCustomButton[];

  private initialize_actions(actions): BaseActionCustomButton[] {

    const result: BaseActionCustomButton[] = []
    for (let action of actions) {
      const initialized_action = get_initialized_action_from_obj(action)
      result.push(initialized_action)
    }
    return result
  }

  public get_action(action: BaseActionCustomButton){
    let existing = this.actions.find(a => a.id === action.id)
    if(!existing){
      return
    }
    const index = this.actions.indexOf(existing)
    return this.actions[index]
  }
  public update_action(action: BaseActionCustomButton){
    let existing = this.actions.find(a => a.id === action.id)
    if(!existing){
      return
    }
    const index = this.actions.indexOf(existing)
    this.actions[index] = action
  }
  public remove_action(action){
    const index = this.actions.indexOf(action);
    if (index > -1) { // only splice array when item is found
      this.actions.splice(index, 1); // 2nd parameter means remove one item only
    }
  }
  public add_action(action: BaseActionCustomButton){
    const initialized = get_initialized_action_from_obj(action)
    this.actions.push(initialized)
  }
  constructor(actions: object[]) {
    if(actions){
      const init_actions = this.initialize_actions(actions)
      this.actions = init_actions;
    }
  }

  async start(annotation_ui_context: BaseAnnotationUIContext, ui_factory_component: AnnotationUIFactory) {
    for (const action of this.actions) {
      await action.execute(annotation_ui_context, ui_factory_component);
    }
  }
}
