import {ImageAnnotationEventCtx, ImageInteractionEvent} from "../../../../types/InteractionEvent";
import {Coordinator, CoordinatorProcessResult} from "../Coordinator";
import {CanvasMouseCtx} from "../../../../types/mouse_position";
import {BoxInstance} from "../../instances/BoxInstance";
import {GLOBAL_SELECTED_COLOR, Instance} from "../../instances/Instance";
import {InstanceImage2D} from "../../instances/InstanceImage2D";
import {CreateInstanceCommand} from "../../../annotation/commands/create_instance_command";

export abstract class ImageAnnotationCoordinator extends Coordinator {
  /*
  * Extends the base coordinator for the context of image annotation.
  * */
  constructor() {
    super();

  }

  instance: InstanceImage2D

  protected is_mouse_down_event(event: ImageInteractionEvent): boolean {
    if (event.dom_event.type === 'mousedown') {
      return true
    }
    return false
  }

  protected is_mouse_up_event(event: ImageInteractionEvent): boolean {
    if (event.dom_event.type === 'mouseup') {
      return true
    }
    return false
  }

  protected is_mouse_move_event(event: ImageInteractionEvent): boolean {
    if (event.dom_event.type === 'mousemove') {
      return true
    }
    return false
  }

  public initialize_instance_drawing(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    let currently_drawing_instance: InstanceImage2D = annotation_event.annotation_ctx.current_drawing_instance as InstanceImage2D
    if (annotation_event.annotation_ctx.video_mode == true) {
      let number = annotation_event.annotation_ctx.current_sequence_from_sequence_component.number;
      let sequence_id = annotation_event.annotation_ctx.current_sequence_from_sequence_component.id;
      currently_drawing_instance.set_sequence_id(sequence_id)
      currently_drawing_instance.set_sequence_number(number)
    }
    currently_drawing_instance.set_label_file_colour_map(annotation_event.annotation_ctx.label_file_colour_map)
    currently_drawing_instance.set_label_file(annotation_event.annotation_ctx.label_file)
    currently_drawing_instance.set_color_from_label()
    currently_drawing_instance.set_canvas(annotation_event.annotation_ctx.canvas_element)
    currently_drawing_instance.set_image_label_settings(annotation_event.annotation_ctx.image_label_settings)
    currently_drawing_instance.set_canvas_transform(annotation_event.annotation_ctx.canvas_transform)

    currently_drawing_instance.set_canvas_mouse_tools(annotation_event.annotation_ctx.canvas_mouse_tools)

    currently_drawing_instance.set_actively_drawing(true)


    coordinator_result.is_actively_drawing = true
  }

  public finish_drawing_instance(instance: InstanceImage2D, coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent) {
    instance.set_color_from_label()
    instance.set_actively_drawing(false)
    const create_box_command = new CreateInstanceCommand(
      instance,
      annotation_event.annotation_ctx.ann_core_ctx,
      annotation_event.annotation_ctx.frame_number
    );
    this.command_manager.executeCommand(create_box_command);
    coordinator_result.is_actively_drawing = false;
    coordinator_result.new_instance_index = annotation_event.annotation_ctx.instance_list.length - 1
  }

  protected should_select_instance(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_down_event(annotation_event) &&
      this.instance &&
      !this.instance.selected &&
      this.instance.is_hovered &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  protected should_deselect_instance(annotation_event: ImageInteractionEvent): boolean {
    return this.is_mouse_down_event(annotation_event) &&
      this.instance &&
      this.instance.selected &&
      !this.instance.is_hovered &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.instance_select_for_issue &&
      !annotation_event.annotation_ctx.view_only_mode
  }

  public select(): void {
    let select_color_stroke = GLOBAL_SELECTED_COLOR;
    this.instance.set_border_color(select_color_stroke);
    this.instance.set_fill_color(255, 255, 255, 0.1);
    this.instance.select()

  }

  public deselect(): void {
    this.instance.set_color_from_label();
    this.instance.unselect()

  }

  public canvas_mouse_ctx: CanvasMouseCtx
}
