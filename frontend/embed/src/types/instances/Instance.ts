import * as THREE from 'three';
import AnnotationScene3D from "../../../../src/components/3d_annotation/AnnotationScene3D";
import {getCenterPoint} from "../../../../src/components/3d_annotation/utils_3d";
import {LabelColourMap} from "../labels/LabelColourMap";
import {LabelFile} from "../labels/Label";
import {MousePosition} from "../annotation/image/MousePosition";
import {ImageCanvasTransform} from "../annotation/image/CanvasTransform";
import {AttributeGroup, AttributeGroupMap} from "../attributes/AttributeGroup";
import {CuboidFace} from "./CuboidInstance";
import {PolygonPoint} from "./PolygonInstance";

export const SUPPORTED_CLASS_INSTANCE_TYPES: Array<string> = ['box', 'keypoints'];
export const GLOBAL_SELECTED_COLOR = '#0000ff'

export interface InstanceBehaviour2D {
  update_min_max_points(): void

  draw(ctx: CanvasRenderingContext2D): void
}


export class Instance {
  public id?: number;

  public initialized: boolean
  public creation_ref_id?: string;
  public action_type?: string;
  public x_min: number;
  public y_min: number;
  public next_id?: number;
  public previous_id?: number;
  public root_id?: number;
  public version?: number;
  public center_x: number;
  public center_y: number;
  public x_max: number;
  public y_max: number;
  public p1: object;
  public cp: object;
  public p2: object;
  public cuboid_current_drawing_face: object;
  public label_file_colour_map: LabelColourMap;
  public nodes: any[] = [];
  public edges: any[] = [];
  public front_face: CuboidFace;
  public angle: number = 0;
  public attribute_groups?: AttributeGroupMap;
  public rear_face: CuboidFace;
  public override_color: string;
  public model_run_id: number;
  public width: number;
  public height: number;
  public label_file: LabelFile;
  public label_file_id: number;
  public selected: boolean = false;
  public number: number;
  public type: string;
  public points: PolygonPoint[] = [];
  public sequence_id: number;
  public soft_delete: boolean = false;
  public is_hovered: boolean = false;
  public is_resizing: boolean = false;
  public interpolated: boolean = false;
  public status: string = '';

  public on_instance_updated?: Function;
  public on_instance_selected?: Function;
  public on_instance_hovered?: Function;
  public on_instance_unhovered?: Function;
  public on_instance_deselected?: Function;
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
    if (this.on_instance_selected) {
      this.on_instance_selected(this)
    }

  }

  public unselect() {
    this.selected = false
    if (this.on_instance_deselected) {
      this.on_instance_deselected(this)
    }

  }

  public populate_from_instance_obj(inst: Instance) {
    for (let key in inst) {
      // @ts-ignore
      this[key] = inst[key]
    }
  }

  public instance_updated_callback(instance: Instance) {
    if (this.on_instance_updated) {
      this.on_instance_updated(instance);
    }
  }

  public delete() {
    this.soft_delete = true;
  }

  public set_label_file(value: LabelFile) {
    this.label_file = value
    this.label_file_id = value.id
  }


  public instance_selected_callback(instance: Instance) {
    if (this.on_instance_selected) {
      this.on_instance_selected(instance);
    }
  }

  public instance_deselected_callback(instance: Instance) {
    if (this.on_instance_deselected) {
      this.on_instance_deselected(instance);
    }
  }


  public on(event_type: string, callback: Function) {
    if (event_type === 'hover_in') {
      this.on_instance_hovered = callback
    }
    if (event_type === 'hover_out') {
      this.on_instance_unhovered = callback
    }
  }

  public remove_listener(event_type: string, callback: Function) {
    if (event_type === 'hover_in') {
      this.on_instance_hovered = undefined
    }
    if (event_type === 'hover_out') {
      this.on_instance_unhovered = undefined
    }
  }
}


