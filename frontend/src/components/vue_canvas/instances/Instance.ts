import * as THREE from 'three';
import AnnotationScene3D from "../../3d_annotation/AnnotationScene3D";
import {getCenterPoint} from "../../3d_annotation/utils_3d";
import {LabelColourMap} from "../../../types/label_colour_map";
import {LabelFile} from "../../../types/label";
import {MousePosition} from "../../../types/mouse_position";
import {ImageCanvasTransform} from "../../../types/CanvasTransform";

export const SUPPORTED_CLASS_INSTANCE_TYPES: Array<string> = ['box', 'keypoints'];
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
  public ctx: CanvasRenderingContext2D;
  public mouse_position: MousePosition;
  public canvas_transform: ImageCanvasTransform;
  public canvas_element: HTMLCanvasElement
  public auto_border_polygon_p1: object = null;
  public auto_border_polygon_p2: object = null;
  public cuboid_current_drawing_face: object = null;
  private label_file_colour_map: LabelColourMap = null;
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
  public strokeColor: string = 'black';
  public fillColor: string = 'white';
  public points: object[] = [];
  public sequence_id: number = null;
  public soft_delete: boolean = false;
  public is_hovered: boolean = false;
  public interpolated: boolean = false;
  public status: string = '';

  public on_instance_updated: Function = undefined;
  public on_instance_selected: Function = undefined;
  public on_instance_hovered: Function = undefined;
  public on_instance_unhovered: Function = undefined;
  public on_instance_deselected: Function = undefined;
  public pause_object: false

  protected is_mouse_in_path(ctx) {
    if (!this.mouse_position || !this.mouse_position.raw) {
      return false
    }
    if (ctx.isPointInPath(
      this.mouse_position.raw.x,
      this.mouse_position.raw.y)) {
      return true;
    }
    return false

  }

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
      strokeColor: this.strokeColor,
      fillColor: this.fillColor,
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
      auto_border_polygon_p1: this.auto_border_polygon_p1,
      auto_border_polygon_p2: this.auto_border_polygon_p2,
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

  public set_color_from_label() {
    console.log('SET COLOR FROM LAEBL', this.get_label_file_colour_map(), this.label_file_id)
    let colour = this.get_label_file_colour_map()[this.label_file_id]
    if (colour) {
      this.set_border_color(colour.hex)
      this.set_fill_color(colour.rgba.r, colour.rgba.g, colour.rgba.b, 0.1)
    }
  }

  public set_border_color(colorHex: string) {
    this.strokeColor = colorHex
  }

  public set_fill_color(r: number, g: number, b: number, a: number) {
    this.fillColor = "rgba(" + r + "," + g + "," + b + "," + a + ")";
  }

  protected grab_color_from_instance(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = this.fillColor
    ctx.strokeStyle = this.strokeColor
  }

  public set_canvas(val: HTMLCanvasElement) {
    this.canvas_element = val
    if (this.canvas_element) {
      this.ctx = this.canvas_element.getContext("2d");
    }
  }

  public set_canvas_transform(val: ImageCanvasTransform) {
    this.canvas_transform = val
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

export abstract class Instance3D extends Instance {
  public helper_lines: THREE.LineSegments;
  public mesh: THREE.Mesh;
  public scene_controller_3d: AnnotationScene3D;
  public geometry: THREE.BoxGeometry;
  public material: THREE.MeshBasicMaterial;
  public depth: number;
  public center_3d: { x: number, y: number, z: number };
  // Rotation is in Euler Angles
  public rotation_euler_angles: { x: number, y: number, z: number };
  public position_3d: { x: number, y: number, z: number };
  public dimensions_3d: { width: number, height: number, depth: number };
  public initialized: boolean;

  abstract draw_on_scene(): void;

  abstract remove_edges(): void;

  public update_spacial_data() {
    var box = new THREE.Box3().setFromObject(this.mesh);
    this.width = box.max.x - box.min.x;
    this.height = box.max.y - box.min.y;
    this.depth = box.max.z - box.min.z;
    let center = getCenterPoint(this.mesh);
    this.center_3d = {
      x: center.x,
      y: center.y,
      z: center.z
    }
    this.rotation_euler_angles = {
      x: this.mesh.rotation.x,
      y: this.mesh.rotation.y,
      z: this.mesh.rotation.z,
    }
    this.position_3d = {
      x: this.mesh.position.x,
      y: this.mesh.position.y,
      z: this.mesh.position.z,
    }

    this.dimensions_3d = {
      width: this.width,
      height: this.height,
      depth: this.depth,
    }

  }

  public delete() {
    super.delete();
    this.mesh.visible = false;
  }

  public get_instance_data() {
    let result = super.get_instance_data();
    return {
      ...result,
      rotation_euler_angles: this.rotation_euler_angles,
      position_3d: this.position_3d,
      dimensions_3d: this.dimensions_3d,
      center_3d: this.center_3d,
      width: 0,
      height: 0,

    }

  }

}
