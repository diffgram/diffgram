import {InteractionEvent} from "./InteractionEvent";


export class Interaction {
  private event_log: InteractionEvent[]
  constructor() {
    this.event_log = []
  }
  public add_event(e: InteractionEvent): InteractionEvent[]{
    this.event_log.push(e)
    return this.event_log
  }
  public get_event_log(): InteractionEvent[]{
    return this.event_log
  }
  public clear_events(): void{
    this.event_log = []
  }
  public get_last_event(): InteractionEvent{
    if (this.event_log.length > 0){
      return this.event_log[this.event_log.length - 1]
    }
    else{
      return
    }
  }


}
