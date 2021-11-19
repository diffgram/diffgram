import * as THREE from 'three';
import {Instance3D} from './Instance'
import SceneController3D from "../../3d_annotation/SceneController3D";

export default class Cuboid3DInstance extends Instance3D {

  public helper_lines: THREE.Mesh;

  public constructor(scene_controller_3d: SceneController3D, mesh: THREE.Mesh) {
    super();
    this.scene_controller_3d = scene_controller_3d;
    this.mesh = mesh;
    this.material = mesh.material;
    this.geometry = mesh.geometry;
    this.type = 'cuboid_3d'
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
      console.log('new meshhhhh')
      this.mesh = new THREE.Mesh( this.geometry, this.material );
      this.mesh.name = 'cuboid_3d'
    }

    this.scene_controller_3d.add_mesh_to_scene(this.mesh, false)
  }

  public highlight_edges(){
    const geometry = this.mesh.geometry.clone();
    const edges = new THREE.EdgesGeometry(geometry);
    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({color: 0xffffff}));

    line.position.copy(this.mesh.position);
    line.rotation.copy(this.mesh.rotation);
    line.scale.copy(this.mesh.scale);

    this.mesh.add(line);
    this.helper_lines = line;
    return line
  }



}
