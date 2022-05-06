
export interface TriggerData {
  trigger_event_name: string,
  upload_directory_id_list: Array<number>,
  trigger_action_id: number,

}
export interface ConditionData {
  event_name: string,

}

export interface CompletionConditionData {
  event_name: string,

}
export class Action {
  public id: number;
  public public_name: string;
  public icon: string;
  public kind: string;
  public trigger_data: TriggerData;
  public condition_data: ConditionData;
  public description: string;
  public completion_condition_data: CompletionConditionData;

  constructor(public_name: string,
              icon: string,
              kind: string,
              trigger_data: TriggerData,
              condition_data: ConditionData,
              description: string,
              complete_condition: CompletionConditionData) {
    this.public_name = public_name;
    this.icon = icon;
    this.kind = kind;
    this.trigger_data = trigger_data;
    this.condition_data = condition_data;
    this.description = description;
    this.completion_condition_data = complete_condition;
  }
}


