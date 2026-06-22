export interface TriggerData {
  event_name: string;
  upload_directory_id_list: number[];
  trigger_action_id: number;
  cron_expression: string;
}

export interface ConditionData {
  event_name: string;
}

export interface CompletionConditionData {
  event_name: string;
}

export interface ConfigData {
  task_template_id: number;
}

export function initializeActionList(actionList: Action[]): Action[] {
  return actionList.map((action) => {
    const newAction = new Action(
      action.public_name,
      action.icon,
      action.kind,
      action.trigger_data,
      action.precondition,
      action.description,
      action.completion_condition_data,
      action.output_interface,
      action.previus_action_output_interface
    );
    if (action.config_data) {
      newAction.config_data = action.config_data;
    }
    return newAction;
  });
}

export class Action {
  public readonly id: number;
  public readonly template_id: number;
  public readonly ordinal: number;
  public readonly public_name: string;
  public readonly archived: boolean;
  public readonly output: any;
  public readonly icon: string;
  public readonly kind: string;
  public readonly trigger_data: TriggerData | {};
  public readonly config_data: ConfigData;
  public readonly precondition: ConditionData | {};
  public readonly description: string;
  public readonly completion_condition_data: CompletionConditionData | {};
  public readonly output_interface: any;
  public readonly previus_action_output_interface: any;

  constructor(
    public_name: string,
    icon: string,
    kind: string,
    trigger_data: TriggerData | {},
    precondition: ConditionData | {},
    description: string,
    completion_condition_data: CompletionConditionData | {},
    output_interface: any = null,
    previus_action_output_interface: any = null
  ) {
    this.public_name = public_name;
    this.icon = icon;
    this.kind = kind;
    this.trigger_data = trigger_data;
    this.precondition = precondition;
    this.description = description;
    this.config_data = {} as ConfigData;
    this.completion_condition_data = completion_condition_data;
    this.output_interface = output_interface;
    this.previus_action_output_interface = previus_action_output_interface;
  }

  public setFromObject(action: any): void {
    if (action.config_data) {
      this.config_data = Object.assign({}, action.config_data);
    }
    this.id = action.id;
    this.template_id = action.template_id;
    this.public_name = action.public_name;
    this.icon = action.icon;
    this.kind = action.kind;
    this.archived = action.archived;
    if (action.trigger_data) {
      this.trigger_data = Object.assign({}, action.trigger_data);
    }
    this.precondition = action.precondition;
    this.ordinal = action.ordinal;
    this.description = action.description;
    this.output = action.output;
    if (action.completion_condition_data) {
      this.completion_condition_data = Object.assign({}, action.completion_condition_data);
    }
  }
}
