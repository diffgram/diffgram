import {InstanceBehaviour2D, Instance} from './Instance'
import {InstanceContext} from './InstanceContext';
import {v4 as uuidv4} from 'uuid';
import {getContrastColor} from '../../../utils/colorUtils'
import {MousePosition} from "../../../types/mouse_position";

export class BoxInstance extends Instance implements InstanceBehaviour2D {
  public mouse_position: MousePosition;
  public ctx: CanvasRenderingContext2D;
  private vertex_size: number = 5;
  private line_width: number = 2;
  private strokeColor: string = 'black';
  private fillColor: string = 'white';
  public is_dragging_instance: boolean = false;
  public is_hovered: boolean = false;
  private is_actively_drawing: boolean = false;
  public is_moving: boolean = false;
  public mouse_down_delta_event: any = undefined;
  public mouse_down_position: any = undefined;
  public initialized: boolean = false;
  private nearest_points_dict: any = undefined
  private zoom_value: number = 1
  private font_size: number = 10



  public get_instance_data(): object {
    const result = super.get_instance_data();
    return result;
  }

  constructor(mouse_position: MousePosition = undefined,
              ctx: CanvasRenderingContext2D = undefined,
              on_instance_updated = undefined,
              on_instance_selected = undefined,
              on_instance_deselected = undefined,
              mouse_down_delta_event = undefined,
              mouse_down_position = undefined) {

    super();
    this.on_instance_updated = on_instance_updated;
    this.on_instance_selected = on_instance_selected;
    this.on_instance_deselected = on_instance_deselected;
    this.mouse_down_delta_event = mouse_down_delta_event;
    this.mouse_down_position = mouse_down_position;
    this.type = 'box'
    this.mouse_position = mouse_position;
    this.initialized = true;
    this.ctx = ctx;
  }
  public set_actively_drawing(val: boolean): void{
    this.is_actively_drawing = val
  }
  public get_is_actively_drawing(): boolean{
    return this.is_actively_drawing;
  }

  public draw(ctx): void {

  }


}
