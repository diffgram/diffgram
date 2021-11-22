import * as THREE from 'three';
import SceneController3D from "../../3d_annotation/SceneController3D";
import {getCenterPoint} from "../../3d_annotation/utils_3d";

export interface InstanceBehaviour {
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
  public auto_border_polygon_p1: object = null;
  public auto_border_polygon_p2: object = null;
  public cuboid_current_drawing_face: object = null;
  public nodes: any[] = [];
  public edges: any[] = [];
  public front_face: object = null;
  public angle: number = 0;
  public attribute_groups: any = null;
  public rear_face: number = null;
  public width: number = null;
  public height: number = null;
  public label_file: object = null;
  public label_file_id: number = null;
  public selected: boolean = false;
  public number: number = null;
  public type: string = null;
  public points: object[] = [];
  public sequence_id: number = null;
  public soft_delete: boolean = false;
  public on_instance_updated: Function = undefined;
  public on_instance_selected: Function = undefined;
  public on_instance_hovered: Function = undefined;
  public on_instance_unhovered: Function = undefined;
  public on_instance_deselected: Function = undefined;
  public pause_object: false


  public get_instance_data(): object {
    /*
    * Specific instance types should add/remove fields to this object if required.
    * */
    return {
      id: this.id,
      creation_ref: this.creation_ref_id,
      x_min: this.x_min,
      y_min: this.y_min,
      center_x: this.center_x,
      center_y: this.center_y,
      x_max: this.x_max,
      y_max: this.y_max,
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
  }

  public unselect() {
    this.selected = false
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

  public instance_hovered_callback(instance) {
    if (this.on_instance_hovered) {
      this.on_instance_hovered(instance)
    }
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

  public instance_unhovered_callback(instance) {
    if (this.on_instance_unhovered) {
      this.on_instance_unhovered(instance);
    }
  }

}

export abstract class Instance3D extends Instance {
  public helper_lines: THREE.Mesh;
  public mesh: THREE.Mesh;
  public scene_controller_3d: SceneController3D;
  public geometry: THREE.BoxGeometry;
  public material: THREE.MeshBasicMaterial;
  public depth: number;
  public center_3d: { x: number, y: number, z: number };
  // Rotation is in Euler Angles
  public rotation_euler_angles: { x: number, y: number, z: number };
  public position_3d: { x: number, y: number, z: number };
  public dimensions_3d: { width: number, height: number, depth: number };

  abstract draw_on_scene(): void;

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
