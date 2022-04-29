
export interface TriggerData {
  trigger_event_name: string,
  upload_directory_id_list: Array<number>,
  trigger_action_id: number,

}
export interface ConditionData {
  condition: string,

}
export class Action {
  public name: string;
  public icon: string;
  public kind: string;
  public trigger_data: TriggerData;
  public condition_data: ConditionData;
  public description: string;
  public complete_condition: string;

  constructor(name: string,
              icon: string,
              kind: string,
              trigger_data: TriggerData,
              condition_data: ConditionData,
              description: string,
              complete_condition: string) {
    this.name = name;
    this.icon = icon;
    this.kind = kind;
    this.trigger_data = trigger_data;
    this.condition_data = condition_data;
    this.description = description;
    this.complete_condition = complete_condition;
  }
}


