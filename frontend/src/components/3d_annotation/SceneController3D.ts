import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import ObjectTransformControls from "./ObjectTransformControls";
import {Instance, Instance3D} from '../vue_canvas/instances/Instance';

export default class SceneController3D{
  public scene: THREE.Scene;
  public controls_orbit: OrbitControls;
  public camera: OrbitControls;
  public renderer: THREE.WebGLRenderer;
  public controls_panning_speed: number;
  public object_transform_controls:  ObjectTransformControls;
  public mouse: THREE.Vector2;
  public raycaster: THREE.Raycaster;
  public draw_mode: THREE.Raycaster;
  public axes_helper: THREE.AxesHelper;
  public grid_helper: THREE.GridHelper;
  public place_holder_cuboid: THREE.Mesh;
  public container: any;
  public excluded_objects_ray_caster: Array<string> = ['axes_helper', 'grid_helper', 'point_cloud'];
  public instance_list: Array<Instance> [];
  public selected_instance: Instance3D = null;

  public constructor(scene, camera, renderer, container, controls_panning_speed = 60) {
    this.scene = scene;
    this.camera = camera;
    this.renderer = renderer;
    this.renderer.setPixelRatio( window.devicePixelRatio );
    this.container = container;
    this.mouse =  new THREE.Vector2();
    this.raycaster = new THREE.Raycaster();

    this.controls_panning_speed = controls_panning_speed
    // Add grid and axis helper arrows
    this.axes_helper = new THREE.AxesHelper(5);
    this.axes_helper.name = 'axes_helper';
    this.grid_helper = new THREE.GridHelper( 1000, 10, 0x888888, 0x444444 )
    this.grid_helper.name = 'grid_helper';

    this.scene.add(this.grid_helper);
    this.scene.add(this.axes_helper);
    this.camera.position.set( 0, 0, 25 );

  }
  private reset_materials(){
    for(const child of this.scene.children){
      if(child.material){
        child.material.opacity = 0.3;
      }
    }
  }

  private on_drag_transform_controls(event){
    this.controls_orbit.enabled = ! event.value;
  }

  private on_mouse_click(event){
    // update the picking ray with the camera and mouse position
    if(this.draw_mode){
      this.on_click_draw_mode(event)
    }
    else{
      this.on_click_edit_mode(event);
    }
  }

  private on_click_draw_mode(event){

  }

  private update_mouse_position(event){
    // calculate mouse position in normalized device coordinates
    // (-1 to +1) for both components
    let canvas = this.renderer.domElement;
    var rect = canvas.getBoundingClientRect(),
      x = event.clientX - rect.left,
      y = event.clientY - rect.top;
    this.mouse.x = ( x / this.container.clientWidth ) * 2 - 1;
    this.mouse.y = - ( y / this.container.clientHeight ) * 2 + 1;
  }

  private on_mouse_move( event ) {

    this.update_mouse_position(event)
    if(this.draw_mode){
      this.draw_place_holder_cuboid();
    }
    else{

    }

  }

  private draw_place_holder_cuboid(){
    console.log('cuboid hoveer')
    if(!this.place_holder_cuboid){
      let geometry = new THREE.BoxGeometry( 2, 2, 2 );
      let material = new THREE.MeshBasicMaterial({
        color: new THREE.Color('red'),
        opacity: 0.7,
        transparent: true,
      });
      this.place_holder_cuboid = new THREE.Mesh( geometry, material );
      this.scene.add(this.place_holder_cuboid)

    }
    // Transform the Mouse 2D Coordinates to the 3D world using unproject()
    let mouse_vector = new THREE.Vector3(this.mouse.x, this.mouse.y, 0.5);
    mouse_vector.unproject( this.camera );
    mouse_vector.sub(this.camera.position).normalize();
    let distance = - this.camera.position.z / mouse_vector.z
    let cube_position = new THREE.Vector3();
    cube_position.copy(this.camera.position).add(mouse_vector.multiplyScalar(distance))
    this.place_holder_cuboid.position.copy(cube_position)

  }

  private check_for_raycaster_picks(){
    // update the picking ray with the camera and mouse position
    this.raycaster.setFromCamera( this.mouse, this.camera );

    // calculate objects intersecting the picking ray
    const intersects = this.raycaster.intersectObjects( this.scene.children.filter(obj => !this.excluded_objects_ray_caster.includes(obj.name)));
    for ( let i = 0; i < intersects.length; i ++ ) {
      intersects[i].object.material.opacity = 0.7;
      intersects[i].object.material.color.set(0xFFFFFF);
    }
  }

  private render(){

    if(this.controls_orbit){
      this.controls_orbit.update();
    }

    requestAnimationFrame( this.render.bind(this) );
    this.reset_materials();
    this.check_for_raycaster_picks();
    this.renderer.render( this.scene, this.camera );

  }

  public attach_mouse_events(){
    window.addEventListener( 'mousemove', this.on_mouse_move.bind(this), false );
    window.addEventListener( 'click', this.on_mouse_click.bind(this) );
  }

  public detach_mouse_events(){
    window.removeEventListener( 'mousemove', this.on_mouse_move.bind(this), false );
  }

  public set_instance_list(instance_list){
    this.instance_list = instance_list;
  }

  public remove_from_scene(object){
    if (!(object instanceof THREE.Object3D)) return false;

    // for better memory management and performance
    object.geometry.dispose();
    if (object.material instanceof Array) {
      // for better memory management and performance
      object.material.forEach(material => material.dispose());
    } else {
      // for better memory management and performance
      object.material.dispose();
    }
    object.removeFromParent(); // the parent might be the scene or another Object3D, but it is sure to be removed this way

    return true;
  }
  public set_draw_mode(draw_mode){
    this.draw_mode = draw_mode;
    if(this.draw_mode){
      this.draw_place_holder_cuboid();
    }
    else{
      this.remove_from_scene(this.place_holder_cuboid);
      this.place_holder_cuboid = null;
    }
  }

  public on_click_edit_mode(event){
    this.raycaster.setFromCamera( this.mouse, this.camera );

    // calculate objects intersecting the picking ray
    const intersects = this.raycaster.intersectObjects( this.scene.children.filter(obj => !this.excluded_objects_ray_caster.includes(obj.name)));
    if(intersects.length > 0){
      console.log('INTERESETXT', intersects[0])
      this.selected_instance = intersects[0].object.userData.currentSquare;
      this.attach_transform_controls_to_mesh(intersects[0].object)
    }
    return intersects;
  }

  public add_cube_to_instance_list(){

  }

  public start_render(){
    this.render();
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
    this.object_transform_controls = new ObjectTransformControls(
      this.camera,
      this.renderer.domElement,
      this.scene,
      this.render.bind(this),
      this.on_drag_transform_controls.bind(this)
    )

  }

  public attach_transform_controls_to_mesh(mesh){
    this.object_transform_controls.attach_to_mesh(mesh)
  }
  public add_mesh_to_scene(mesh, center_camera_to_object = true){

    if(center_camera_to_object){
      mesh.rotateX(THREE.Math.degToRad(-90));
      mesh.rotateY(THREE.Math.degToRad(0));
      mesh.rotateZ(THREE.Math.degToRad(0));
      let center = mesh.geometry.boundingSphere.center;



    }
    this.scene.add(mesh);
  }
}
