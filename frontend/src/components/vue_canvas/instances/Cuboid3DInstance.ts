import * as THREE from 'three';
import {Instance3D} from './Instance'
import SceneController3D from "../../3d_annotation/SceneController3D";

export default class Cuboid3DInstance extends Instance3D {

  scene_controller_3d: SceneController3D;
  mesh: THREE.Mesh;
  geometry: THREE.BoxGeometry;
  material: THREE.MeshBasicMaterial;

  public constructor(scene_controller_3d: SceneController3D, mesh: THREE.Mesh) {
    super();
    this.scene_controller_3d = scene_controller_3d;
    this.mesh = mesh;
    this.material = mesh.material;
    this.geometry = mesh.geometry;
  }

  public draw_on_scene(){
    if(!this.material){
      this.geometry = new THREE.BoxGeometry( 2, 2, 2 );
    }
    if(!this.geometry){
      this.material = new THREE.MeshBasicMaterial({
        color: new THREE.Color('red'),
        opacity: 0.3,
        transparent: true,
      });
    }
    if(!this.mesh){
      this.mesh = new THREE.Mesh( this.geometry, this.material );
      this.mesh.name = 'cuboid_3d'
    }

    this.scene_controller_3d.add_mesh_to_scene(this.mesh, false)
  }



}
