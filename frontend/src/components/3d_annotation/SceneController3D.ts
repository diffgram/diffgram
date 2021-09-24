import * as THREE from 'three';
import { OrbitControls } from './OrbitControls';
import ObjectTransformControls from "./ObjectTransformControls";
import {Instance, Instance3D} from '../vue_canvas/instances/Instance';
import Cuboid3DInstance from "../vue_canvas/instances/Cuboid3DInstance";

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
  public component_ctx: object;
  public label_file: object = null;
  public container: any;
  public excluded_objects_ray_caster: Array<string> = ['axes_helper', 'grid_helper', 'point_cloud'];
  public instance_list: Array<Instance3D> =  [];
  public selected_instance: Instance3D = null;
  public TRANSFORM_CONTROLS_LAYER: number = 1;

  public constructor(scene, camera, renderer, container, component_ctx, instance_list, controls_panning_speed = 60) {
    this.scene = scene;
    this.camera = camera;
    this.renderer = renderer;
    this.renderer.setPixelRatio( window.devicePixelRatio );
    this.container = container;
    this.component_ctx = component_ctx;
    this.mouse =  new THREE.Vector2();
    this.instance_list =  instance_list
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
    this.camera.layers.enable(this.TRANSFORM_CONTROLS_LAYER)

  }
  private reset_materials(){
    if(this.draw_mode){
      return
    }
    for(const child of this.scene.children){
      if(child.material){
        let instance_index = child.userData.instance_index;
        child.material.opacity = 0.3;
        child.material.color.set(child.userData.color)
        let instance = this.instance_list[instance_index];
        if(this.selected_instance){
          if(this.selected_instance.mesh === child){
            child.material.color.set(0xFFFFFF)
            child.material.opacity = 0.5;
          }
        }

      }
    }
  }

  private get_current_color(){
    if(this.label_file){
      return this.label_file.colour.hex;
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

  private on_mouse_double_click(event){
    event.stopPropagation();
    if(this.draw_mode){
      this.on_double_click_draw_mode(event)
    }
    else{
      this.on_double_click_edit_mode(event)
    }
  }



  private on_double_click_edit_mode(event){
    if(this.object_transform_controls){
      this.deselect_instance()
    }

  }

  private on_double_click_draw_mode(event){
    if(this.place_holder_cuboid){
      // Add cuboid to instance list
      let new_instance = this.add_cube_to_instance_list(this.place_holder_cuboid);
      this.place_holder_cuboid = null;
      this.select_instance(new_instance);
      this.set_draw_mode(false);


      if(this.component_ctx){
        this.component_ctx.$emit('instance_drawn', new_instance)
      }
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
        color: new THREE.Color(this.get_current_color()),
        opacity: 0.9,
        transparent: true,
      });
      this.place_holder_cuboid = new THREE.Mesh( geometry, material );
      this.scene.add(this.place_holder_cuboid)

    }
    // Transform the Mouse 2D Coordinates to the 3D world using unproject()
    let mouse_vector = new THREE.Vector3(this.mouse.x, this.mouse.y, 0.5  );
    mouse_vector.unproject( this.camera );
    mouse_vector.sub(this.camera.position).normalize();
    let distance = - this.camera.position.z / mouse_vector.z
    let cube_position = new THREE.Vector3();
    cube_position.copy(this.camera.position).add(mouse_vector.multiplyScalar(distance))
    this.place_holder_cuboid.position.copy(cube_position)

  }

  private check_hover(){
    if(this.draw_mode){
      return
    }
    // update the picking ray with the camera and mouse position
    this.raycaster.setFromCamera( this.mouse, this.camera );

    // calculate objects intersecting the picking ray
    const intersects = this.raycaster.intersectObjects( this.scene.children.filter(obj => !this.excluded_objects_ray_caster.includes(obj.name)));
    for ( let i = 0; i < intersects.length; i ++ ) {
      intersects[i].object.material.opacity = 0.5;
      intersects[i].object.material.color.set(0xFFFFFF);
    }
  }

  private render(){

    requestAnimationFrame( this.render.bind(this) );
    this.reset_materials();
    this.check_hover();
    this.renderer.render( this.scene, this.camera );

  }

  public attach_mouse_events(){
    window.addEventListener( 'mousemove', this.on_mouse_move.bind(this), false );
    window.addEventListener( 'click', this.on_mouse_click.bind(this) );
    window.addEventListener( 'dblclick', this.on_mouse_double_click.bind(this) );
  }

  public detach_mouse_events(){
    window.removeEventListener( 'mousemove', this.on_mouse_move.bind(this), false );
  }

  public set_instance_list(instance_list){
    this.instance_list = instance_list;
  }

  public set_current_label_file(label_file){
    this.label_file = label_file;
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
      if(this.object_transform_controls){
        this.object_transform_controls.detach_controls();
      }
    }
    else{
      this.remove_from_scene(this.place_holder_cuboid);

      this.place_holder_cuboid = null;
    }
  }

  public deselect_instance(){
    if(!this.selected_instance){
      return
    }
    this.selected_instance.mesh.remove(...this.selected_instance.mesh.children);
    this.remove_from_scene(this.selected_instance.helper_lines)
    this.selected_instance.helper_lines = null;
    this.selected_instance = null;
    this.object_transform_controls.detach_controls();

  }

  public select_instance(instance){
    // Build the White Edges Box (To highlight edge lines of cuboid)
    const geometry = instance.mesh.geometry.clone();
    const edges = new THREE.EdgesGeometry( geometry );
    const line = new THREE.LineSegments( edges, new THREE.LineBasicMaterial( { color: 0xffffff } ) );

    line.position.copy(instance.mesh.position);
    line.rotation.copy(instance.mesh.rotation);
    line.scale.copy(instance.mesh.scale);

    instance.mesh.add(line);
    this.attach_transform_controls_to_mesh(instance.mesh)
    if(this.component_ctx){
      this.component_ctx.$emit('instance_selected', instance)
    }
    this.selected_instance = instance;
    this.selected_instance.helper_lines = line;
    this.scene.add(line);
  }

  public on_click_edit_mode(event){
    this.raycaster.setFromCamera( this.mouse, this.camera );

    // calculate objects intersecting the picking ray
    const intersects = this.raycaster.intersectObjects( this.scene.children.filter(obj => !this.excluded_objects_ray_caster.includes(obj.name)));
    if(intersects.length > 0){
      let index = intersects[0].object.userData.instance_index
      let instance_to_select = this.instance_list[index];
      if(instance_to_select){
        this.select_instance(instance_to_select)
      }


    }
    return intersects;
  }

  public add_cube_to_instance_list(cuboid_mesh){
    let new_instance = new Cuboid3DInstance(
      this,
      cuboid_mesh
    )
    new_instance.label_file = this.label_file;
    new_instance.label_file_id = this.label_file.id;
    new_instance.draw_on_scene()
    this.instance_list.push(new_instance);
    let index = this.instance_list.length - 1;
    new_instance.mesh.userData.instance_index = index;
    new_instance.mesh.userData.color = this.label_file.colour.hex;
    return new_instance
  }

  public start_render(){
    this.render();
  }




  public add_orbit_controls(){
    this.controls_orbit = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls_orbit.listenToKeyEvents( window ); // optional
    this.controls_orbit.enableDamping = false; // an animation loop is required when either damping or auto-rotation are enabled
    this.controls_orbit.dampingFactor = 0.09;
    this.controls_orbit.screenSpacePanning = true;
    this.controls_orbit.enableRotate = true;
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
      this,
      this.renderer.domElement,
      this.scene,
      this.render.bind(this),
      this.on_drag_transform_controls.bind(this),
      this.TRANSFORM_CONTROLS_LAYER
    )

  }

  public attach_transform_controls_to_mesh(mesh){
    this.object_transform_controls.attach_to_mesh(mesh)
    console.log('attach controlss')
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
