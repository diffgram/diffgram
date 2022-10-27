import {Coordinator, CoordinatorProcessResult} from "../../Coordinator";
import {BoxInstance} from "../../../instances/BoxInstance";
import {
  InteractionEvent,
  ImageAnnotationEventCtx,
  ImageInteractionEvent
} from "../../../../../types/InteractionEvent";
import {ImageAnnotationCoordinator} from "../ImageAnnotationCoordinator";
import {duplicate_instance} from "../../../../../utils/instance_utils";
import {CanvasMouseCtx} from "../../../../../types/mouse_position";
import {CreateInstanceCommand} from "../../../../annotation/commands/create_instance_command";
import CommandManager from "../../../../../helpers/command/command_manager";
import {InstanceColor} from "../../../../../types/instance_color";

export class BoxInstanceCoordinator extends ImageAnnotationCoordinator {
  /**
   * Routes an annotation_event and interaction of a user to box instances.
   * */
  box_instance: BoxInstance
  original_edit_instance: BoxInstance

  constructor(box_instance, canvas_mouse_ctx: CanvasMouseCtx, command_manager: CommandManager) {
    super();
    this.box_instance = box_instance
    this.canvas_mouse_ctx = canvas_mouse_ctx
    this.command_manager = command_manager
  }



  private should_start_drawing_box(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_down_event(annotation_event) &&
      !this.box_instance &&
      !annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
  }

  private should_resize_new_box(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_move_event(annotation_event)
      && annotation_event.annotation_ctx.current_drawing_instance
      && annotation_event.annotation_ctx.is_actively_drawing
      && annotation_event.annotation_ctx.draw_mode
  }

  private save_original_instance_for_undo(){
    if (!this.original_edit_instance) {
      this.original_edit_instance = duplicate_instance(this.box_instance, this.canvas_mouse_ctx)
      // this.original_edit_instance_index = i;
    }
  }

  private start_drawing_box(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent): void {
    let currently_drawing_box: BoxInstance = annotation_event.annotation_ctx.current_drawing_instance as BoxInstance
    currently_drawing_box.set_actively_drawing(true)
    currently_drawing_box.set_canvas(annotation_event.annotation_ctx.canvas_element)
    currently_drawing_box.set_label_file(annotation_event.annotation_ctx.label_file)
    currently_drawing_box.set_canvas_transform(annotation_event.annotation_ctx.canvas_transform)
    currently_drawing_box.set_label_file_colour_map(annotation_event.annotation_ctx.label_file_colour_map)
    currently_drawing_box.set_color_from_label()

    coordinator_result.is_actively_drawing = true
  }

  private do_new_box_resize(annotation_event: ImageInteractionEvent){
    let box_instance = annotation_event.annotation_ctx.current_drawing_instance as BoxInstance
    if(annotation_event.annotation_ctx.view_issue_mode){
      // When viewing an issue we will not allow moving/resizing of instances
      box_instance.set_mouse_cursor_from_hovered_point('blocked')
      return
    }

    box_instance.resize_from_mouse_position(
      annotation_event.dom_event,
      annotation_event.annotation_ctx.mouse_position,
      annotation_event.annotation_ctx.mouse_down_position,
    )
  }
  private should_finish_box_drawing(annotation_event: ImageInteractionEvent): boolean {
    console.log('annotation_event.annotation_ctx.draw_mode', annotation_event.annotation_ctx.draw_mode)
    console.log('annotation_event.annotation_ctx.current_drawing_instance', annotation_event.annotation_ctx.current_drawing_instance)
    console.log('annotation_event.annotation_ctx.is_actively_drawing', annotation_event.annotation_ctx.is_actively_drawing)
    return this.is_mouse_up_event(annotation_event) &&
      annotation_event.annotation_ctx.current_drawing_instance &&
      annotation_event.annotation_ctx.draw_mode &&
      annotation_event.annotation_ctx.current_drawing_instance.width > 0 &&
      annotation_event.annotation_ctx.current_drawing_instance.height > 0 &&
      annotation_event.annotation_ctx.is_actively_drawing
  }

  private should_select_instance(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_down_event(annotation_event) &&
      this.box_instance &&
      !this.box_instance.selected &&
      this.box_instance.is_hovered &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  private finish_box_drawing(result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent): void {

    let box = annotation_event.annotation_ctx.current_drawing_instance as BoxInstance
    console.log('finish box drawing', box)
    box.set_actively_drawing(false)
    const create_box_command = new CreateInstanceCommand(
      box,
      annotation_event.annotation_ctx.ann_core_ctx,
      annotation_event.annotation_ctx.frame_number
    );
    this.command_manager.executeCommand(create_box_command);
    result.new_instance_index = annotation_event.annotation_ctx.instance_list.length - 1

  }

  private select_box(result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent): void {
    let box = annotation_event.annotation_ctx.current_drawing_instance as BoxInstance;
    let select_color_stroke = '#0000ff';
    box.set_border_color(select_color_stroke);
    box.set_fill_color(0,0,255, 1);
    box.select()

  }

  public perform_action_from_event(annotation_event: ImageInteractionEvent): CoordinatorProcessResult {
    let result: CoordinatorProcessResult = {
      instance_moved: false,
      is_actively_drawing: annotation_event.annotation_ctx.is_actively_drawing,
    }

    if (this.should_start_drawing_box(annotation_event)) {
      this.start_drawing_box(result, annotation_event)
    }
    if(this.should_resize_new_box(annotation_event)){
      this.do_new_box_resize(annotation_event)
    }

    if(this.should_finish_box_drawing(annotation_event)){
      this.finish_box_drawing(result, annotation_event)
    }

    if (this.should_select_instance(annotation_event)) {
      this.select_box(result, annotation_event)
    }

    return result
  }

}
