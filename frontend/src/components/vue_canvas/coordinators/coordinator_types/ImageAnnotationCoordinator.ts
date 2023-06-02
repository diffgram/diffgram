import {ImageAnnotationEventCtx, ImageInteractionEvent} from "../../../../types/InteractionEvent";
import {Coordinator, CoordinatorProcessResult} from "../Coordinator";
import {CanvasMouseCtx} from "../../../../types/mouse_position";
import {BoxInstance} from "../../instances/BoxInstance";
import {GLOBAL_SELECTED_COLOR, Instance} from "../../instances/Instance";
import {InstanceImage2D} from "../../instances/InstanceImage2D";
import {CreateInstanceCommand} from "../../../annotation/image_and_video_annotation/commands/create_instance_command";
import {UpdateInstanceCommand} from "../../../annotation/image_and_video_annotation/commands/update_instance_command";
import {PolygonInstance} from "../../instances/PolygonInstance";

export abstract class ImageAnnotationCoordinator extends Coordinator {
  /*
  * Extends the base coordinator for the context of image annotation.
  * */
  public canvas_mouse_ctx: CanvasMouseCtx
  instance: InstanceImage2D

  constructor() {
    super();

  }

  private is_mouse_event(event: MouseEvent | KeyboardEvent): event is MouseEvent {
    const mouse_events = ['dblclick', 'mousedown', 'mouseup', 'mousemove']

    return mouse_events.includes(event.type)
  }

  protected is_mouse_double_click_event(event: ImageInteractionEvent): boolean {
    if (event.dom_event.type === 'dblclick') {
      return true
    }
    return false
  }

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

  protected is_keyup_enter_event(event: ImageInteractionEvent): boolean {
    if (!this.is_mouse_event(event.dom_event) && event.dom_event.keyCode === 13) {
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
    let allow_select_in_merge = true;
    let instance = this.instance as InstanceImage2D
    let polygon_merge_tool = annotation_event.annotation_ctx.polygon_merge_tool
    if (polygon_merge_tool) {
      let hover_index = annotation_event.annotation_ctx.instance_hover_index
      let hovered_instance = annotation_event.annotation_ctx.instance_list[hover_index] as PolygonInstance
      allow_select_in_merge = polygon_merge_tool.is_allowed_instance_to_merge(hovered_instance)
      if(allow_select_in_merge){
        instance = hovered_instance
      }
    }


    return this.is_mouse_down_event(annotation_event) &&
      instance &&
      !instance.selected &&
      instance.is_hovered &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.view_only_mode &&
      allow_select_in_merge
  }

  protected should_deselect_instance(annotation_event: ImageInteractionEvent): boolean {
    let allow_select_in_merge = true;
    let polygon_merge_tool = annotation_event.annotation_ctx.polygon_merge_tool
    let instance = this.instance
    if (polygon_merge_tool) {
      instance = instance as PolygonInstance
      let hover_index = annotation_event.annotation_ctx.instance_hover_index
      let hovered_instance = annotation_event.annotation_ctx.instance_list[hover_index] as PolygonInstance
      allow_select_in_merge = annotation_event.annotation_ctx.polygon_merge_tool.is_allowed_instance_to_merge(hovered_instance)
      if (allow_select_in_merge) {
        instance = hovered_instance
      }
    }
    // Deselection Allowed in issue creation mode
    if(this.is_mouse_down_event(annotation_event) &&
      instance &&
      instance.selected
      && annotation_event.annotation_ctx.instance_select_for_issue){
      return true
    }

    const result = (this.is_mouse_down_event(annotation_event) &&
      instance &&
      instance.selected &&
      (annotation_event.annotation_ctx.polygon_merge_tool &&
        annotation_event.annotation_ctx.polygon_merge_tool.parent_merge_instance !== this.instance) &&
      (!instance.is_hovered ) &&
      !annotation_event.annotation_ctx.draw_mode &&
      !annotation_event.annotation_ctx.view_issue_mode &&
      !annotation_event.annotation_ctx.view_only_mode
    )
    return result
  }

  public select(annotation_event: ImageInteractionEvent): void {
    let select_color_stroke = GLOBAL_SELECTED_COLOR;
    this.instance.set_border_color(select_color_stroke);
    this.instance.set_fill_color(255, 255, 255, 0.1);
    this.instance.select()

  }

  public deselect(annotation_event: ImageInteractionEvent): void {
    this.instance.set_color_from_label();
    this.instance.unselect()

  }

  protected edit_instance_command_creation(annotation_event: ImageInteractionEvent, result: CoordinatorProcessResult) {
    const new_instance = this.instance;
    const command = new UpdateInstanceCommand(
      new_instance,
      annotation_event.annotation_ctx.instance_list.indexOf(new_instance),
      annotation_event.annotation_ctx.original_edit_instance,
      annotation_event.annotation_ctx.ann_core_ctx
    );
    this.command_manager.executeCommand(command);
    result.original_edit_instance = undefined;
  }
}
