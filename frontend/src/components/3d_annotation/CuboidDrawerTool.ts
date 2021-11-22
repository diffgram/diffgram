import * as THREE from 'three';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls';
import SceneController3D from "./SceneController3D";

export default class CuboidDrawerTool {
  public scene_controller: SceneController3D;
  public place_holder_cuboid: THREE.Mesh;
  public mouse_position_3d_initial_draw: THREE.Vector3;

  public constructor(scene_controller) {
    this.scene_controller = scene_controller;
    this.mouse_position_3d_initial_draw = new THREE.Vector3();
    this.place_holder_cuboid = null;

  }

  public create_place_holder_cuboid(){
    if (!this.place_holder_cuboid) {

      var box = new THREE.Box3().setFromObject( this.scene_controller.point_cloud_mesh );
      let size = Math.abs(box.max - box.min)


      // let geometry = new THREE.BoxGeometry(size * 0.05, size * 0.05, size * 0.05);
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
    let scaleFactorX = xSize / this.place_holder_cuboid.geometry.parameters.width;
    let scaleFactorY = ySize / this.place_holder_cuboid.geometry.parameters.height;
    let scaleFactorZ = zSize / this.place_holder_cuboid.geometry.parameters.depth;
    this.place_holder_cuboid.scale.set( scaleFactorX, scaleFactorY, scaleFactorZ );
    this.scene_controller.render()

  }


}
