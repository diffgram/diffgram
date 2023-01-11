import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import ObjectTransformControls from "./ObjectTransformControls";
import {Instance3D} from '../../vue_canvas/instances/Instance3D';
import {Instance} from '../../vue_canvas/instances/Instance';
import Cuboid3DInstance from "../../vue_canvas/instances/Cuboid3DInstance";
import AnnotationScene3D from "./AnnotationScene3D";
import {getCenterPoint} from './utils_3d'

export default class AnnotationScene3DOrtographicView extends  AnnotationScene3D{
  public camera: THREE.OrthographicCamera;

  public constructor(scene, camera, renderer, container, component_ctx, instance_list, controls_panning_speed = 60, point_cloud_mesh) {
    super(scene, camera, renderer, container, component_ctx, instance_list, controls_panning_speed, point_cloud_mesh)

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

  public on_click_edit_mode(event): void{
    return
  }

  public attach_transform_controls_to_mesh(mesh){
    return
  }

  public center_camera_to_mesh(mesh, axis = 'x', offset = 1): void{
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
