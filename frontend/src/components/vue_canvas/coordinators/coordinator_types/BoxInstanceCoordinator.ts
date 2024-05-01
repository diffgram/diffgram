import { Coordinator, CoordinatorProcessResult } from "../Coordinator";
import { BoxInstance } from "../../instances/BoxInstance";
import {
  InteractionEvent,
  ImageAnnotationEventCtx,
  ImageInteractionEvent
} from "../../../../types/InteractionEvent";
import { ImageAnnotationCoordinator } from "./ImageAnnotationCoordinator";
import { duplicate_instance } from "../../../../utils/instance_utils";
import { CanvasMouseCtx } from "../../../../types/mouse_position";
import CommandManager from "../../../../helpers/command/command_manager";
import { InstanceColor } from "../../../../types/instance_color";

export class BoxInstanceCoordinator extends ImageAnnotationCoordinator {
  /**
   * Routes annotation_event and interaction of a user to box instances.
   */
  constructor(box_instance: BoxInstance, canvas_mouse_ctx: CanvasMouseCtx, command_manager: CommandManager) {
    super();
    this.instance = box_instance;
    this.canvas_mouse_ctx = canvas_mouse_ctx;
    this.command_manager = command_manager;
  }

  // ... (Other methods)

  private start_drawing_box(coordinator_result: CoordinatorProcessResult, annotation_event: ImageInteractionEvent): void {
    this.initialize_instance_drawing(coordinator_result, annotation_event);
  }

  // ... (Other methods)

  private edit_instance_command_creation(annotation_event: ImageInteractionEvent, result: CoordinatorProcessResult) {
    // Create a command for editing the instance
    const command = new CommandManager.EditInstanceCommand(
      this.instance,
      this.canvas_mouse_ctx,
      annotation_event.annotation_ctx,
      result.original_edit_instance,
      this.command_manager
    );

    // Execute the command
    command.execute();
  }

  // ... (Other methods)

  public perform_action_from_event(annotation_event: ImageInteractionEvent): CoordinatorProcessResult {
    // ... (Initialization)

    // Route event to box drawing
    this.route_event_to_box_drawing(annotation_event, result);

    // Handle box select
    if (this.should_select_instance(annotation_event)) {
      this.select(annotation_event);
    } else if (this.should_deselect_instance(annotation_event)) {
      this.deselect(annotation_event);
    }

    // Handle box drag
    if (this.should_start_moving_box(annotation_event)) {
      this.start_box_move(result);
    } else if (this.should_drag_box(annotation_event)) {
      this.do_box_drag(result);
    } else if (this.should_stop_moving_box(annotation_event)) {
      this.stop_box_move(annotation_event, result);
    }

    // Handle box resize
    if (this.should_start_resizing_box(annotation_event)) {
      this.start_box_resize(result);
    } else if (this.should_stop_resizing_box(annotation_event)) {
      this.stop_box_resize(annotation_event, result);
    } else if (this.should_resize_box(annotation_event)) {
      this.do_box_resize(annotation_event, result);
    }

    return result;
  }
}
