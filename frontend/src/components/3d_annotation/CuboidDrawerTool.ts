import * as THREE from 'three';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls';
import AnnotationScene3D from "./AnnotationScene3D";
import {Instance3D} from "../vue_canvas/instances/Instance";

export default class CuboidDrawerTool {
  public scene_controller: AnnotationScene3D;
  public place_holder_cuboid: THREE.Mesh;
  public mouse_position_3d_initial_draw: THREE.Vector3;

  public constructor(scene_controller) {
    this.scene_controller = scene_controller;
    this.mouse_position_3d_initial_draw = new THREE.Vector3();
    this.place_holder_cuboid = null;

  }

  public create_place_holder_cuboid(){
    if (!this.place_holder_cuboid) {
      let geometry = new THREE.BoxGeometry(1, 1, 1);
      this.mouse_position_3d_initial_draw = this.mouse_position_3d_initial_draw.copy(this.scene_controller.mouse_position_3d)
      let material = new THREE.MeshBasicMaterial({
        // color: new THREE.Color(this.get_current_color()),
        color: new THREE.Color(this.scene_controller.get_current_color()),
        opacity: 0.7,
        transparent: true,

      });
      this.place_holder_cuboid = new THREE.Mesh(geometry, material);
      this.place_holder_cuboid.position.copy(this.mouse_position_3d_initial_draw)
      this.scene_controller.scene.add(this.place_holder_cuboid)

    }
  }

  public create_mesh_from_instance_data(instance: Instance3D){
    let geometry = new THREE.BoxGeometry(
      instance.dimensions_3d.width,
      instance.dimensions_3d.height,
      instance.dimensions_3d.depth
    );
    const pos = new THREE.Vector3(
      instance.position_3d.x,
      instance.position_3d.y,
      instance.position_3d.z
    );
    let material = new THREE.MeshBasicMaterial({
      // color: new THREE.Color(this.get_current_color()),
      color: new THREE.Color(instance.label_file.colour.hex),
      opacity: 0.7,
      transparent: true,

    });
    let mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(pos)
    return mesh;
  }

  public remove_placeholder_cuboid(){
    this.place_holder_cuboid = null;
  }

  public resize_place_holder_cuboid() {
    if(!this.place_holder_cuboid){
      return
    }

    let mouse_position_3d = this.scene_controller.mouse_position_3d;

    let xSize = mouse_position_3d.x - this.mouse_position_3d_initial_draw.x;
    let ySize = mouse_position_3d.y - this.mouse_position_3d_initial_draw.y;
    let zSize = Math.max(xSize, ySize);
    let geometry = this.place_holder_cuboid.geometry as THREE.BoxGeometry;
    let scaleFactorX = xSize / geometry.parameters.width;
    let scaleFactorY = ySize / geometry.parameters.height;
    let scaleFactorZ = zSize / geometry.parameters.depth;
    this.place_holder_cuboid.scale.set( scaleFactorX, scaleFactorY, scaleFactorZ );
    this.scene_controller.render()

  }


}
