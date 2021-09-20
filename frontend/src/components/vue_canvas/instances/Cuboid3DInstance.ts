import * as THREE from 'three';
import {Instance} from './Instance'
import SceneController3D from "../../3d_annotation/SceneController3D";

export default class Cuboid3DInstance extends Instance {

  scene_controller_3d: SceneController3D;
  mesh: THREE.Mesh;
  geometry: THREE.BoxGeometry;
  material: THREE.MeshBasicMaterial;

  public constructor(scene_controller_3d: SceneController3D, x, y) {
    super();
    this.scene_controller_3d = scene_controller_3d;
    this.center_x = x;
    this.center_y = y;
  }

  public draw_on_scene(){
    let render = this.scene_controller_3d.render;
    let renderer = this.scene_controller_3d.renderer;

    this.geometry = new THREE.BoxGeometry( 2, 2, 2 );
    this.material = new THREE.MeshBasicMaterial({
      color: new THREE.Color('red'),
      opacity: 0.7,
      transparent: true,
    });

    this.mesh = new THREE.Mesh( this.geometry, this.material );
    this.scene_controller_3d.add_mesh_to_scene(this.mesh, false)
  }


}
