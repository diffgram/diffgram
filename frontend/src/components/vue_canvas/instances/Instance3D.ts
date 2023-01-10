import * as THREE from "three";
import AnnotationScene3D from "../../annotation/3d_annotation/AnnotationScene3D";
import {getCenterPoint} from "../../annotation/3d_annotation/utils_3d";
import {Instance} from "./Instance";

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
