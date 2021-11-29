import * as THREE from 'three';
import {Instance3D} from './Instance'
import SceneController3D from "../../3d_annotation/SceneController3D";
import {v4 as uuidv4 } from 'uuid'

export default class Cuboid3DInstance extends Instance3D {

  public helper_lines: THREE.LineSegments;
  public material: THREE.MeshBasicMaterial;
  public geometry: THREE.BoxGeometry;


  public constructor(scene_controller_3d: SceneController3D, mesh: THREE.Mesh) {
    super();
    this.scene_controller_3d = scene_controller_3d;
    this.mesh = mesh;
    this.material = mesh.material as THREE.MeshBasicMaterial;
    this.geometry = mesh.geometry as THREE.BoxGeometry;
    this.type = 'cuboid_3d'
    this.initialized = true;
    this.creation_ref_id = uuidv4();
  }

  public draw_on_scene(){
    if(!this.material && !this.mesh){
      this.geometry = new THREE.BoxGeometry( 2, 2, 2 );
    }
    if(!this.geometry && !this.mesh){
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

  public highlight_edges(){
    const geometry = this.mesh.geometry.clone();
    const edges = new THREE.EdgesGeometry(geometry);
    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({color: 0xffffff}));

    line.position.copy(this.mesh.position);
    line.rotation.copy(this.mesh.rotation);
    line.scale.copy(this.mesh.scale);
    line.renderOrder = 1;
    //
    this.helper_lines = line;
    this.mesh.add(line);
    this.scene_controller_3d.scene.add(line);
    return line
  }

  public remove_edges(){
    this.mesh.remove(this.helper_lines);
    this.scene_controller_3d.remove_from_scene(this.helper_lines)
    this.helper_lines = null;

  }

  public copy_mesh(){
    const geometry = this.mesh.geometry.clone();
    let material = new THREE.MeshBasicMaterial({
      color: new THREE.Color(this.scene_controller_3d.get_current_color()),
      opacity: 0.7,
      transparent: true,


    });

    let mesh = new THREE.Mesh(geometry, material);

    return mesh;
  }



}
