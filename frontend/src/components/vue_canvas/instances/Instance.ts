import * as THREE from 'three';
import AnnotationScene3D from "../../annotation/3d_annotation/AnnotationScene3D";
import {getCenterPoint} from "../../annotation/3d_annotation/utils_3d";
import {LabelColourMap} from "../../../types/label_colour_map";
import {LabelFile} from "../../../types/label";
import {MousePosition, Point} from "../../../types/mouse_position";
import {ImageCanvasTransform} from "../../../types/CanvasTransform";
import {PolygonPoint} from "./PolygonInstance";

export const SUPPORTED_IMAGE_CLASS_INSTANCE_TYPES: Array<string> = ['box', 'keypoints', 'polygon'];
export const GLOBAL_SELECTED_COLOR = '#0000ff'
export interface InstanceBehaviour2D {
  update_min_max_points(): void

  draw(ctx): void
}


export class Instance {
  public id: number = null;
  public creation_ref_id: string = null;
  public x_min: number = null;
  public y_min: number = null;
  public center_x: number = null;
  public center_y: number = null;
  public x_max: number = null;
  public y_max: number = null;
  public p1: object = null;
  public cp: object = null;
  public p2: object = null;

  public cuboid_current_drawing_face: object = null;
  public label_file_colour_map: LabelColourMap = null;
  public nodes: any[] = [];
  public edges: any[] = [];
  public front_face: object = null;
  public angle: number = 0;
  public attribute_groups: any = null;
  public rear_face: number = null;
  public override_color: string = null;
  public model_run_id: number = null;
  public width: number = null;
  public height: number = null;
  public label_file: LabelFile;
  public label_file_id: number = null;
  public selected: boolean = false;
  public number: number = null;
  public type: string = null;
  public points: PolygonPoint[] = [];
  public sequence_id: number = null;
  public soft_delete: boolean = false;
  public is_hovered: boolean = false;
  public is_resizing: boolean = false;
  public interpolated: boolean = false;
  public status: string = '';

  public on_instance_updated: Function = undefined;
  public on_instance_selected: Function = undefined;
  public on_instance_hovered: Function = undefined;
  public on_instance_unhovered: Function = undefined;
  public on_instance_deselected: Function = undefined;
  public pause_object: false


  public set_label_file_colour_map(map: LabelColourMap): void {
    this.label_file_colour_map = map
  }

  public get_label_file_colour_map(): LabelColourMap {
    return this.label_file_colour_map
  }

  // Returns any just to avoid warnings in the new Command pattern related class. Need to be replaces with the interface
  public get_instance_data(): any {
    /*
    * Specific instance types should add/remove fields to this object if required.
    * */
    return {
      id: this.id,
      creation_ref_id: this.creation_ref_id,
      attribute_groups: this.attribute_groups,
      x_min: this.x_min,
      y_min: this.y_min,
      center_x: this.center_x,
      center_y: this.center_y,
      x_max: this.x_max,
      y_max: this.y_max,
      label_file_colour_map: this.label_file_colour_map,
      p1: this.p1,
      cp: this.cp,
      p2: this.p2,
      cuboid_current_drawing_face: this.cuboid_current_drawing_face,
      nodes: this.nodes,
      edges: this.edges,
      front_face: this.front_face,
      angle: this.angle,
      rear_face: this.rear_face,
      width: this.width,
      height: this.height,
      label_file: this.label_file,
      label_file_id: this.label_file_id,
      selected: this.selected,
      number: this.number,
      type: this.type,
      points: this.points,
      sequence_id: this.sequence_id,
      soft_delete: this.soft_delete,
      pause_object: this.pause_object,
    }
  }

  public select() {
    this.selected = true
    this.on_instance_selected(this)
  }

  public unselect() {
    this.selected = false
    this.on_instance_deselected(this)
  }

  public populate_from_instance_obj(inst) {
    for (let key in inst) {
      this[key] = inst[key]
    }
  }

  public instance_updated_callback(instance) {
    if (this.on_instance_updated) {
      this.on_instance_updated(instance);
    }
  }

  public delete() {
    this.soft_delete = true;
  }

  public set_label_file(value: LabelFile) {
    if(!value){
      return
    }
    this.label_file = value
    this.label_file_id = value.id
  }


  public instance_selected_callback(instance) {
    if (this.on_instance_selected) {
      this.on_instance_selected(instance);
    }
  }

  public instance_deselected_callback(instance) {
    if (this.on_instance_deselected) {
      this.on_instance_deselected(instance);
    }
  }


  public on(event_type: string, callback: Function) {
    if(event_type === 'hover_in'){
      this.on_instance_hovered = callback
    }
    if(event_type === 'hover_out'){
      this.on_instance_unhovered = callback
    }
  }
  public remove_listener(event_type: string, callback: Function) {
    if(event_type === 'hover_in'){
      this.on_instance_hovered = null
    }
    if(event_type === 'hover_out'){
      this.on_instance_unhovered = null
    }
  }
}


