import {BaseActionCustomButton} from "./BaseActionCustomButton";
import {ActionSetAttributeValue} from "./button_actions/ActionSetAttributeValue";
import {ActionCompleteTask} from "./button_actions/ActionCompleteTask";

export const CUSTOM_BUTTON_ACTION_TYPE = {
  set_attribute: 'set_attribute',
  complete_task: 'complete_task',
}
export class CustomButtonWorkflow {
  private actions: BaseActionCustomButton[];

  private initialize_actions(actions): BaseActionCustomButton[] {
    const action_types_map = {
      [CUSTOM_BUTTON_ACTION_TYPE.set_attribute]: ActionSetAttributeValue,
      [CUSTOM_BUTTON_ACTION_TYPE.complete_task]: ActionCompleteTask,
    }
    const result: BaseActionCustomButton[] = []
    for (let action of actions) {
      const initialized_action = new action_types_map[action.type]({
        metadata: action.metadata,
        type: action.type,
        name: action.name,
        workflow: this,
      })
      result.push(initialized_action)
    }
    return result
  }

  constructor(actions: object[]) {
    const init_actions = this.initialize_actions(actions)
    this.actions = init_actions;
  }

  async start() {
    for (const action of this.actions) {
      await action.execute();
    }
  }
}
