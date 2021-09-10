import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

export default class SceneController3D{
  public scene: THREE.Scene;
  public orbit_controls: OrbitControls;

  public constructor(scene, orbit_controls, controls_speed = 30) {
    this.scene = scene
    this.orbit_controls = orbit_controls
    this.orbit_controls.keyPanSpeed = controls_speed
  }

  public add_mesh_to_scene(mesh, center_camera_to_object = true){

    if(center_camera_to_object){
      mesh.rotateX(THREE.Math.degToRad(0));
      mesh.rotateY(THREE.Math.degToRad(180));
      mesh.rotateZ(THREE.Math.degToRad(45));
      // let center = mesh.geometry.boundingSphere.center;
      // this.orbit_controls.target.set(center.x, center.y, center.z);
      // this.orbit_controls.update();
    }
    this.scene.add(mesh);
  }
}
