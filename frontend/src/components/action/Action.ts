
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
export interface ConfigData{
  task_template_id: number
}
export const initialize_action_list = function(action_list){
  let res = []
  for(let act of action_list){
    let action = new Action(
      act.public_name,
      act.icon,
      act.kind,
      act.trigger_data,
      act.condition_data,
      act.description,
      act.completion_condition_data
    )
    action.id = act.id
    if(act.config_data){
      action.config_data = act.config_data
    }
    res.push(action)
  }
  return res
}
export class Action {
  public id: number;
  public public_name: string;
  public icon: string;
  public kind: string;
  public trigger_data: TriggerData;
  public config_data: ConfigData;
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
    this.config_data = {};
    this.completion_condition_data = complete_condition;
  }
}


