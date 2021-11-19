import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import ObjectTransformControls from "./ObjectTransformControls";
import {Instance, Instance3D} from '../vue_canvas/instances/Instance';
import Cuboid3DInstance from "../vue_canvas/instances/Cuboid3DInstance";
import SceneController3D from "./SceneController3D";
import {getCenterPoint} from './utils_3d'

export default class SceneControllerOrtographicView extends  SceneController3D{
  public constructor(scene, camera, renderer, container, component_ctx, instance_list, controls_panning_speed = 60) {
    super(scene, camera, renderer, container, component_ctx, controls_panning_speed, instance_list)

    // Hide the 3D transform controls layer. Because here we'll use 2D bounding box
    this.camera.layers.disable(this.TRANSFORM_CONTROLS_LAYER);
  }

  public add_orbit_controls() {
    super.add_orbit_controls();

    // this.controls_orbit.maxPolarAngle = Math.PI/ 2;
    this.controls_orbit.enableRotate = false;
    this.controls_orbit.update();
  }

  public add_transform_controls(){
    return
  }

  public on_click_edit_mode(){
    return
  }

  public attach_transform_controls_to_mesh(mesh){
    return
  }

  public center_camera_to_mesh(mesh, axis = 'x'){
    let center = getCenterPoint(mesh);
    let frustrum_height;
    var aspect = this.container.clientWidth / this.container.clientHeight;
    var helper_bbox = new THREE.BoxHelper(mesh);
    helper_bbox.update();
    var bbox_radius = helper_bbox.geometry.boundingSphere.radius;
    if(aspect > 1){
      frustrum_height = 2 * bbox_radius;
    }
    else{
      frustrum_height = 2 * bbox_radius / aspect;
    }
    if(axis === 'x'){

      this.camera.position.set(center.x - 20, center.y, center.z);
      this.camera.lookAt(center);

      this.camera.left = - frustrum_height * aspect / 2;
      this.camera.right = frustrum_height * aspect / 2;
      this.camera.top = frustrum_height / 2;
      this.camera.bottom = - frustrum_height / 2;
      this.camera.updateProjectionMatrix();


    }
    if(axis === 'y'){
      this.camera.position.set(center.x, center.y - 20, center.z);
      this.camera.lookAt(center);

      this.camera.left = - frustrum_height * aspect / 2;
      this.camera.right = frustrum_height * aspect / 2;
      this.camera.top = frustrum_height / 2;
      this.camera.bottom = - frustrum_height / 2;
      this.camera.updateProjectionMatrix();

    }
    if(axis === 'z'){
      this.camera.position.set(center.x, center.y, center.z - 20);
      this.camera.lookAt(center);

      this.camera.left = - frustrum_height * aspect / 2;
      this.camera.right = frustrum_height * aspect / 2;
      this.camera.top = frustrum_height / 2;
      this.camera.bottom = - frustrum_height / 2;
      this.camera.updateProjectionMatrix();

    }
    this.render();
  }
}
