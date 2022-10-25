import {Coordinator, CoordinatorProcessResult} from "../../Coordinator";
import {BoxInstance} from "../../../instances/BoxInstance";
import {
  AnnotationToolEvent,
  ImageAnnotationEventCtx,
  ImageAnnotationToolEvent
} from "../../../../../types/AnnotationToolEvent";
import {ImageAnnotationCoordinator} from "../ImageAnnotationCoordinator";
import {duplicate_instance} from "../../../../../utils/instance_utils";
import {CanvasMouseCtx} from "../../../../../types/mouse_position";

export class BoxInstanceCoordinator extends ImageAnnotationCoordinator {
  /**
   * Routes an annotation_event and interaction of a user to box instances.
   * */
  box_instance: BoxInstance
  original_edit_instance: BoxInstance

  constructor(box_instance, canvas_mouse_ctx: CanvasMouseCtx) {
    super();
    this.box_instance = box_instance
    this.canvas_mouse_ctx = canvas_mouse_ctx
  }

  private is_mouse_down_event(event: ImageAnnotationToolEvent): boolean {
    if (event.dom_event.type === 'mousedown') {
      return true
    }
    return false
  }
  private is_mouse_move_event(event: ImageAnnotationToolEvent): boolean {
    if (event.dom_event.type === 'mousemove') {
      return true
    }
    return false
  }

  private should_start_drawing_box(annotation_event: ImageAnnotationToolEvent): boolean {
    return this.is_mouse_down_event(annotation_event) && !this.box_instance && !annotation_event.annotation_ctx.is_actively_drawing
  }

  private should_resize_new_box(annotation_event: ImageAnnotationToolEvent): boolean {
    console.log('is_mouse_move_event', this.is_mouse_move_event(annotation_event))
    console.log(' annotation_event.annotation_ctx.is_actively_drawing',  annotation_event.annotation_ctx.is_actively_drawing)
    console.log('current_drawing_instance', annotation_event.annotation_ctx.current_drawing_instance )
    return this.is_mouse_move_event(annotation_event) && annotation_event.annotation_ctx.current_drawing_instance && annotation_event.annotation_ctx.is_actively_drawing
  }

  private save_original_instance_for_undo(){
    if (!this.original_edit_instance) {
      this.original_edit_instance = duplicate_instance(this.box_instance, this.canvas_mouse_ctx)
      // this.original_edit_instance_index = i;
    }
  }

  private start_drawing_box(coordinator_result: CoordinatorProcessResult, annotation_event: ImageAnnotationToolEvent): void {
    let currently_drawing_box: BoxInstance = annotation_event.annotation_ctx.current_drawing_instance as BoxInstance
    currently_drawing_box.set_actively_drawing(true)
    currently_drawing_box.set_canvas(annotation_event.annotation_ctx.canvas_element)
    currently_drawing_box.set_canvas_transform(annotation_event.annotation_ctx.canvas_transform)
    currently_drawing_box.set_label_file_colour_map(annotation_event.annotation_ctx.label_file_colour_map)
    coordinator_result.is_actively_drawing = true
  }

  private do_box_resize(annotation_event: ImageAnnotationToolEvent){
    if(this.annotation_event.view_issue_mode){
      // When viewing an issue we will not allow moving/resizing of instances
      this.box_instance.set_mouse_cursor_from_hovered_point('blocked')
      return
    }
    let movement_point_hover = this.box_instance.determine_movement_point_for_box()
    this.box_instance.set_mouse_cursor_from_hovered_point(movement_point_hover)
    this.box_instance.resize_from_mouse_position(
      annotation_event.dom_event,
      annotation_event.annotation_ctx.mouse_position
    )
  }
  public perform_action_from_event(annotation_event: ImageAnnotationToolEvent): CoordinatorProcessResult {
    let result: CoordinatorProcessResult = {
      instance_moved: false
    }
    console.log(
      'AAAAAANN EVENT', annotation_event
    )
    console.log('this.should_resize_new_box()', this.should_resize_new_box(annotation_event))
    if (this.should_start_drawing_box(annotation_event)) {
      this.start_drawing_box(result, annotation_event)
    }
    if(this.should_resize_new_box(annotation_event)){
      this.do_box_resize(annotation_event)
    }
    return result
  }

}
