import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls';

export default class SceneController3D{
  public scene: THREE.Scene;
  public controls_orbit: OrbitControls;
  public controls_transform: TransformControls;
  public camera: OrbitControls;
  public renderer: THREE.WebGLRenderer;
  public controls_panning_speed: number;

  public constructor(scene, camera, renderer, controls_panning_speed = 60) {
    this.scene = scene
    this.camera = camera
    this.renderer = renderer

    this.controls_panning_speed = controls_panning_speed
    // Add grid and axis helper arrows
    this.scene.add( new THREE.AxesHelper( 5 ) );
    this.scene.add( new THREE.GridHelper( 1000, 1000, 0x888888, 0x444444 ) );
  }

  public start_render(){
    this.render();
  }

  public render(){

    if(this.controls_orbit){
      this.controls_orbit.update();
    }

    requestAnimationFrame( this.render.bind(this) );
    this.renderer.render( this.scene, this.camera );

  }
  public add_orbit_controls(){
    this.controls_orbit = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls_orbit.listenToKeyEvents( window ); // optional
    this.controls_orbit.enableDamping = true; // an animation loop is required when either damping or auto-rotation are enabled
    this.controls_orbit.dampingFactor = 0.09;
    this.controls_orbit.screenSpacePanning = true;
    this.controls_orbit.keyPanSpeed = this.controls_panning_speed
    this.controls_orbit.minDistance = 0;
    this.controls_orbit.maxDistance = 99999;

    // this.controls_orbit.maxPolarAngle = Math.PI/ 2;

    this.controls_orbit.keys = {
      LEFT: 'KeyA'  , //left arrow
      UP: 'KeyW', // up arrow
      RIGHT: 'KeyD', // right arrow
      BOTTOM: 'KeyS' // down arrow
    }
  }

  public add_transform_controls(){
    this.controls_transform = new TransformControls( this.camera, this.renderer.domElement );
    this.controls_transform.addEventListener( 'change', this.render );
    let parent_scope = this;
    this.controls_transform.addEventListener( 'dragging-changed', function ( event ) {

      parent_scope.controls_orbit.enabled = ! event.value;

    } );
  }
  public add_mesh_to_scene(mesh, center_camera_to_object = true){

    if(center_camera_to_object){
      // mesh.geometry.center();
      mesh.rotateX(THREE.Math.degToRad(-90));
      mesh.rotateY(THREE.Math.degToRad(0));
      mesh.rotateZ(THREE.Math.degToRad(0));
      let center = mesh.geometry.boundingSphere.center;
      this.camera.position.set( center.x + 25, center.y + 25, center.z + 25);
      this.camera.lookAt( center.x, center.y, center.z );

    }
    this.scene.add(mesh);
  }
}
