import {AnnotationToolEvent} from "./AnnotationToolEvent";


export class Interaction {
  private event_log: AnnotationToolEvent[]
  constructor() {
    this.event_log = []
  }
  public add_event(e: AnnotationToolEvent): AnnotationToolEvent[]{
    this.event_log.push(e)
    return this.event_log
  }
  public get_event_log(): AnnotationToolEvent[]{
    return this.event_log
  }
  public clear_events(): void{
    this.event_log = []
  }
  public get_last_event(): AnnotationToolEvent{
    if (this.event_log.length > 0){
      return this.event_log[this.event_log.length - 1]
    }
    else{
      return
    }
  }


}
