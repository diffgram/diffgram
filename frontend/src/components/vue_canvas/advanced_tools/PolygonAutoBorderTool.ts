import {PolygonInstance, PolygonPoint} from "../../../../embed/src/types/instances/PolygonInstance";
import {CoordinatorProcessResult} from "../coordinators/Coordinator";
import {ImageInteractionEvent} from "../../../types/InteractionEvent";
import {Instance} from "../instances/Instance";


export type AutoBorderContext = {
  auto_border_polygon_p1: PolygonPoint
  auto_border_polygon_p2: PolygonPoint
  auto_border_polygon_p1_index: number
  auto_border_polygon_p2_index: number

  auto_border_polygon_p1_instance_index: number
  auto_border_polygon_p2_instance_index: number

  auto_border_polygon_p1_figure: string
  auto_border_polygon_p2_figure: string

  show_snackbar_auto_border: boolean
  show_polygon_border_context_menu: boolean
}

export class PolygonAutoBorderTool {
  context: AutoBorderContext

  public constructor(auto_border_context: AutoBorderContext) {
    this.context = auto_border_context
  }
  private find_auto_border_point(points: PolygonPoint[], instance_index: number) {
    let found_point = false;
    let point_index = 0;
    for (const point of points) {
      if (point.hovered_while_drawing) {
        if (!this.context.auto_border_polygon_p1) {
          this.context.auto_border_polygon_p1 = point;
          this.context.auto_border_polygon_p1_index = point_index;
          this.context.auto_border_polygon_p1_figure = point.figure_id;
          this.context.auto_border_polygon_p1_instance_index = instance_index;
          point.point_set_as_auto_border = true;
          found_point = true;
          this.context.show_snackbar_auto_border = true;
          break;
        } else if (
          !this.context.auto_border_polygon_p2 &&
          point != this.context.auto_border_polygon_p1 &&
          instance_index === this.context.auto_border_polygon_p1_instance_index
        ) {
          this.context.auto_border_polygon_p2 = point;
          this.context.auto_border_polygon_p2_index = point_index;
          this.context.auto_border_polygon_p2_figure = point.figure_id;
          point.point_set_as_auto_border = true;
          this.context.auto_border_polygon_p2_instance_index = instance_index;
          this.context.show_snackbar_auto_border = false;
          found_point = true;
          break;
        }
      }
      point_index += 1;
    }
    return found_point;
  }

  public polygon_auto_border_set_indexes(instance_list: Instance[], current_poly: PolygonInstance) {

    if (!this.context.auto_border_polygon_p1 && this.context.auto_border_polygon_p2) {
      return;
    }
    let found_point = false;
    for (let instance_index = 0; instance_index < instance_list.length; instance_index++) {
      const polygon = instance_list[instance_index] as PolygonInstance;
      if (polygon.type !== "polygon" || polygon.soft_delete) {
        continue;
      }

      let points = polygon.points;
      let figure_list = polygon.get_polygon_figures();

      if (figure_list.length === 0) {
        let autoborder_point_exists = this.find_auto_border_point(
          points,
          instance_index
        );
        if (autoborder_point_exists) {
          found_point = true;
        }
      } else {
        for (const figure_id of figure_list) {
          points = polygon.points.filter((p) => p.figure_id === figure_id);
          let autoborder_point_exists = this.find_auto_border_point(
            points,
            instance_index
          );
          if (autoborder_point_exists) {
            found_point = true;
          }
        }
      }
      if (found_point) {
        break;
      }
    }
    if (this.context.auto_border_polygon_p1_index != undefined && this.context.auto_border_polygon_p2_index != undefined) {
      this.context.show_polygon_border_context_menu = true;
      current_poly.show_active_drawing_mouse_point = false
    }
  }
  public reset_auto_border_context(){
    this.context.auto_border_polygon_p1 = undefined;
    this.context.auto_border_polygon_p1_index = undefined;
    this.context.auto_border_polygon_p1_figure = undefined;
    this.context.auto_border_polygon_p1_instance_index = undefined;
    this.context.auto_border_polygon_p2 = undefined;
    this.context.auto_border_polygon_p2_index = undefined;
    this.context.auto_border_polygon_p2_figure = undefined;
    this.context.auto_border_polygon_p2_instance_index = undefined;
    this.context.show_polygon_border_context_menu = false;
  }
  public reset_instance_points(instance_list: Instance[]){
    for (let inst of instance_list){
      if(inst.type === 'polygon'){
        for(let point of inst.points){
          point.point_set_as_auto_border = false
          point.hovered_while_drawing = false
        }
      }
    }
  }
  public perform_auto_bordering(path_type: string, instance_list: Instance[], current_drawing_instance: PolygonInstance){
    let current_polygon_point_list = current_drawing_instance.points as PolygonPoint[]
    const auto_border_polygon =
      instance_list[this.context.auto_border_polygon_p2_instance_index];
    let points = auto_border_polygon.points;
    if (this.context.auto_border_polygon_p1_figure) {
      points = auto_border_polygon.points.filter(
        (p) => p.figure_id === this.context.auto_border_polygon_p1_figure
      );
    }

    // Forward Path
    let current_index = this.context.auto_border_polygon_p1_index;
    let forward_count = 0;
    let forward_index_list = [];
    while (current_index != this.context.auto_border_polygon_p2_index) {
      // Don't add p1 index
      if (current_index !== this.context.auto_border_polygon_p1_index) {
        forward_index_list.push(current_index);
      }
      if (current_index >= points.length) {
        current_index = 0;
        forward_count += 1;
        continue;
      }
      current_index += 1;
      forward_count += 1;
    }

    // Backwards path
    current_index = this.context.auto_border_polygon_p1_index;
    let backward_count = 0;
    let backward_index_list = [];
    while (current_index != this.context.auto_border_polygon_p2_index) {
      // Don't add p1 index
      if (current_index !== this.context.auto_border_polygon_p1_index) {
        backward_index_list.push(current_index);
      }
      if (current_index < 0) {
        current_index = points.length;
        backward_count += 1;
        continue;
      }
      current_index -= 1;
      backward_count += 1;
    }
    const longest = forward_count > backward_count ? "forward" : "backward";
    const shortest = forward_count <= backward_count ? "forward" : "backward";
    if (path_type === "long_path") {
      if (longest === "forward") {
        for (const index of forward_index_list) {
          if (points[index] == undefined) {
            continue;
          }
          current_polygon_point_list.push({
            ...points[index],
            figure_id: undefined,
          });
        }
      } else {
        for (const index of backward_index_list) {
          if (points[index] == undefined) {
            continue;
          }
          current_polygon_point_list.push({
            ...points[index],
            figure_id: undefined,
          });
        }
      }
    } else {
      if (shortest === "forward") {
        for (const index of forward_index_list) {
          if (points[index] == undefined) {
            continue;
          }
          current_polygon_point_list.push({
            ...points[index],
            figure_id: undefined,
          });
        }
      } else {
        for (const index of backward_index_list) {
          if (points[index] == undefined) {
            continue;
          }
          current_polygon_point_list.push({
            ...points[index],
            figure_id: undefined,
          });
        }
      }
    }

    current_polygon_point_list.push({
      ...this.context.auto_border_polygon_p2,
      figure_id: undefined,
    });
    this.reset_auto_border_context()
    this.reset_instance_points(instance_list)
    current_drawing_instance.show_active_drawing_mouse_point = true
  }
}
