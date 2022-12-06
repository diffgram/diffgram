import {InteractionEvent} from "../annotation/InteractionEvent";
import CommandManager from "../../../../src/helpers/command/command_manager";
import {Instance} from "../instances/Instance";
import {AutoBorderContext} from "../advanced_tools/PolygonAutoBorderTool";

export type CoordinatorProcessResult = {
  instance_moved?: boolean
  is_actively_drawing?: boolean
  lock_point_hover_change?: boolean
  new_instance_index?: number
  polygon_point_click_index?: number
  polygon_point_hover_index?: number
  new_instance?: Instance
  original_edit_instance?: Instance
  instance_hover_index?: number
  instance_hover_type?: string
  locked_editing_instance?: Instance
  auto_border_context?: AutoBorderContext

}

export abstract class Coordinator {
  public type: string
  public command_manager: CommandManager

  abstract perform_action_from_event(ann_tool_event: InteractionEvent): CoordinatorProcessResult

}
