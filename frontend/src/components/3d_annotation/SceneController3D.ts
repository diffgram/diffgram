import * as THREE from 'three';
import {OrbitControls} from './OrbitControls';
import ObjectTransformControls from "./ObjectTransformControls";
import CuboidDrawerTool from "./CuboidDrawerTool";
import {Instance, Instance3D} from '../vue_canvas/instances/Instance';
import Cuboid3DInstance from "../vue_canvas/instances/Cuboid3DInstance";
import {getCenterPoint} from "./utils_3d";
import Vue from 'vue';

export default class SceneController3D {
  public scene: THREE.Scene;
  public controls_orbit: OrbitControls;
  public camera: THREE.PerspectiveCamera | THREE.OrthographicCamera;
  public renderer: THREE.WebGLRenderer;
  public controls_panning_speed: number;
  public object_transform_controls: ObjectTransformControls;
  public mouse: THREE.Vector2;
  public raycaster: THREE.Raycaster;
  public draw_mode: THREE.Raycaster;
  public axes_helper: THREE.AxesHelper;
  public grid_helper: THREE.GridHelper;

  public component_ctx: Vue;
  public label_file: { id: number, label: any, label_file: any, colour: {hex: string} } = null;
  public mouse_position_3d: THREE.Vector3;

  public plane_normal: THREE.Vector3;
  public plane: THREE.Plane;
  public point_cloud_mesh: THREE.Mesh;
  public cuboid_drawer_tool: CuboidDrawerTool;
  public mouse_position_2d: THREE.Vector2;
  public container: any;
  public animation_id: any;
  public excluded_objects_ray_caster: Array<string> = ['axes_helper', 'grid_helper', 'point_cloud'];
  public instance_list: Array<Instance3D> = [];
  public selected_instance: Instance3D = null;
  public currently_drawing_instance: boolean = false;
  public selected_instance_index: number = null;
  public instance_hovered_index: number = null;
  public TRANSFORM_CONTROLS_LAYER: number = 1;
  public scene_width: number = null;
  public scene_height: number = null;
  public scene_depth: number = null;

  public constructor(scene, camera, renderer, container, component_ctx, instance_list, controls_panning_speed = 60, point_cloud_mesh: THREE.Mesh) {
    this.scene = scene;
    this.camera = camera;
    this.renderer = renderer;
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.container = container;
    this.component_ctx = component_ctx;
    this.mouse = new THREE.Vector2();
    this.plane_normal = new THREE.Vector3();
    this.mouse_position_3d = new THREE.Vector3();
    this.plane = new THREE.Plane();
    this.instance_list = instance_list
    this.point_cloud_mesh = point_cloud_mesh
    this.raycaster = new THREE.Raycaster();
    this.controls_panning_speed = controls_panning_speed

    // Add grid and axis helper arrows
    this.axes_helper = new THREE.AxesHelper(5);
    this.axes_helper.name = 'axes_helper';
    this.grid_helper = new THREE.GridHelper(1000, 10, 0x888888, 0x444444)
    this.grid_helper.name = 'grid_helper';

    this.scene.add(this.grid_helper);
    this.scene.add(this.axes_helper);
    this.camera.layers.enable(this.TRANSFORM_CONTROLS_LAYER)

    this.cuboid_drawer_tool = new CuboidDrawerTool(this)
  }

  public clear_all(initial_obj = undefined) {
    let obj = initial_obj;
    if (!initial_obj) {
      obj = this.scene;
    }
    cancelAnimationFrame(this.animation_id);
    while (obj.children.length) {
      this.clear_all(obj.children[0]);
      obj.remove(obj.children[0]);
    }
    if (obj.geometry) obj.geometry.dispose();

    if (obj.material) {
      //in case of map, bumpMap, normalMap, envMap ...
      Object.keys(obj.material).forEach(prop => {
        if (!obj.material[prop])
          return;
        if (obj.material[prop] !== null && typeof obj.material[prop].dispose === 'function')
          obj.material[prop].dispose();
      })
      obj.material.dispose();
    }
    this.renderer.setAnimationLoop(null);
    while (this.renderer.domElement.lastChild) {
      this.renderer.domElement.removeChild(this.renderer.domElement.lastChild)
    } // `renderer` is stored earlier
    this.scene = undefined;
  }

  private reset_materials() {
    if (this.draw_mode) {
      return
    }
    if (!this.scene) {
      return
    }
    for (let child_elm of this.scene.children) {
      let child = child_elm as THREE.Mesh
      if (child.material) {

        let instance_index = child.userData.instance_index;
        (child.material as THREE.MeshBasicMaterial).opacity = 0.6;
        (child.material as THREE.MeshBasicMaterial).color.set(child.userData.color)
        let instance = this.instance_list[instance_index];
        if (this.selected_instance) {
          if (this.selected_instance.mesh === child) {
            (child.material as THREE.MeshBasicMaterial).opacity = 0.9;
          }
        }

      }
    }
  }

  public get_current_color() {
    if (this.label_file) {
      return this.label_file.colour.hex;
    }
  }

  private on_drag_transform_controls(event) {
    this.controls_orbit.enabled = !event.value;
  }

  private on_mouse_click(event) {
    // update the picking ray with the camera and mouse position

    if (this.draw_mode) {
      this.on_click_draw_mode(event)
    } else {
      this.on_click_edit_mode(event);
    }
  }

  private on_mouse_double_click(event) {
    event.stopPropagation();
    if (this.draw_mode) {
      this.on_double_click_draw_mode(event)
    } else {
      this.on_double_click_edit_mode(event)
    }
  }


  private on_double_click_edit_mode(event) {
    if (this.object_transform_controls) {
      this.deselect_instance()
    }

  }

  private on_double_click_draw_mode(event) {
    if (this.draw_mode && !this.currently_drawing_instance) {
      this.currently_drawing_instance = true;
      this.cuboid_drawer_tool.create_place_holder_cuboid();
    }

  }

  private on_click_draw_mode(event) {
    if (!this.scene) {
      return
    }

    if (this.currently_drawing_instance) {
      if (this.cuboid_drawer_tool.place_holder_cuboid) {
        this.currently_drawing_instance = false;
        // Add cuboid to instance list
        this.set_draw_mode(false);
        let new_instance = this.add_cube_to_instance_list(this.cuboid_drawer_tool.place_holder_cuboid);

        this.select_instance(new_instance, this.instance_list.length - 1);

        this.cuboid_drawer_tool.remove_placeholder_cuboid()


        if (this.component_ctx) {
          this.component_ctx.$emit('instance_drawn', new_instance)
        }
      }


    } else {

    }

    // this.create_mini_sphere()

  }

  private update_mouse_position(event) {
    // calculate mouse position in normalized device coordinates
    // (-1 to +1) for both components
    let canvas = this.renderer.domElement;
    var rect = canvas.getBoundingClientRect(),
      x = event.clientX - rect.left,
      y = event.clientY - rect.top;

    this.mouse.x = (x / this.container.clientWidth) * 2 - 1;
    this.mouse.y = -(y / this.container.clientHeight) * 2 + 1;
    this.get_3d_mouse_position();
    this.component_ctx.$emit('updated_mouse_position',
      {
        x: this.mouse.x,
        y: this.mouse.y,
        screen_y: y,
        screen_x: x
      }
    )
  }

  private on_mouse_move(event) {

    this.update_mouse_position(event);
    if (this.draw_mode) {
      if (this.currently_drawing_instance) {
        this.cuboid_drawer_tool.resize_place_holder_cuboid();
      }

    } else {

    }

  }

  private get_3d_mouse_position() {
    // Transform the Mouse 2D Coordinates to the 3D world using unproject()
    this.plane_normal.copy(this.camera.position).normalize();
    this.plane.setFromNormalAndCoplanarPoint(this.plane_normal, this.scene.position);
    this.raycaster.setFromCamera(this.mouse, this.camera);
    let inter_point = this.raycaster.ray.intersectPlane(this.plane, this.mouse_position_3d);
    return this.mouse_position_3d
  }


  private check_hover() {
    if (this.draw_mode) {
      return
    }
    if (!this.scene) {
      return
    }
    // update the picking ray with the camera and mouse position
    this.raycaster.setFromCamera(this.mouse, this.camera);

    // calculate objects intersecting the picking ray
    const intersects = this.raycaster.intersectObjects(this.scene.children.filter(obj => !this.excluded_objects_ray_caster.includes(obj.name)));
    let hovered_instance = false;
    let was_hovered = this.instance_hovered_index != undefined;
    for (let i = 0; i < intersects.length; i++) {
      let object = intersects[i].object as THREE.Mesh;
      (object.material as THREE.MeshBasicMaterial).opacity = 0.5;
      // intersects[i].object.material.color.set(0xFFFFFF);
      if (object.userData.instance_index != undefined) {
        this.instance_hovered_index = object.userData.instance_index
        let instance = this.instance_list[this.instance_hovered_index];
        this.component_ctx.$emit('instance_hovered', instance, this.instance_hovered_index);
        hovered_instance = true
      }
    }
    if (!hovered_instance && was_hovered) {
      this.instance_hovered_index = null
      this.component_ctx.$emit('instance_unhovered');
    }
  }

  private animate() {
    if (!this.scene) {
      return
    }
    this.animation_id = requestAnimationFrame(this.animate.bind(this));

    this.render();
  }

  public render() {
    if (!this.scene) {
      return
    }
    this.reset_materials();
    this.check_hover();
    this.renderer.render(this.scene, this.camera);

  }

  public attach_mouse_events() {
    if(!this.container){
      return
    }
    this.container.addEventListener('mousemove', this.on_mouse_move.bind(this), false);
    this.container.addEventListener('click', this.on_mouse_click.bind(this));
    this.container.addEventListener('dblclick', this.on_mouse_double_click.bind(this));
  }

  public detach_mouse_events() {
    if(!this.container){
      return
    }
    this.container.removeEventListener('mousemove', this.on_mouse_move.bind(this));
    this.container.removeEventListener('click', this.on_mouse_click.bind(this));
    this.container.removeEventListener('dblclick', this.on_mouse_double_click.bind(this));
  }

  public set_instance_list(instance_list) {
    this.instance_list = instance_list;
  }

  public set_current_label_file(label_file) {
    this.label_file = label_file;
  }

  public remove_from_scene(object) {
    if (!(object instanceof THREE.Object3D)) return false;

    // for better memory management and performance
    // object.geometry.dispose();
    // if (object.material instanceof Array) {
    //   // for better memory management and performance
    //   object.material.forEach(material => material.dispose());
    // } else {
    //   // for better memory management and performance
    //   object.material.dispose();
    // }
    object.removeFromParent(); // the parent might be the scene or another Object3D, but it is sure to be removed this way

    return true;
  }

  public set_draw_mode(draw_mode) {


    let placeholder_cuboid = this.cuboid_drawer_tool.place_holder_cuboid;
    if (this.draw_mode) {
      if (this.object_transform_controls && this.selected_instance) {
        this.detach_controls_from_mesh();
      }
      if (this.currently_drawing_instance) {
        this.remove_from_scene(placeholder_cuboid);
        this.cuboid_drawer_tool.remove_placeholder_cuboid()
      }
    } else {
      this.remove_from_scene(placeholder_cuboid);
      this.cuboid_drawer_tool.remove_placeholder_cuboid()
    }
    this.currently_drawing_instance = false;
    this.draw_mode = draw_mode;
  }


  public deselect_instance() {
    console.log(this.selected_instance, 'deselectttt');
    if (!this.selected_instance) {
      return
    }

    this.selected_instance.remove_edges();
    this.selected_instance = null;
    this.selected_instance_index = null;
    this.detach_controls_from_mesh();

  }

  public select_instance(instance, index) {
    // Build the White Edges Box (To highlight edge lines of cuboid)
    let line = instance.highlight_edges();


    this.attach_transform_controls_to_mesh(instance.mesh)

    instance.selected = true;
    instance.status = 'updated';
    this.selected_instance = instance;
    this.selected_instance_index = index;
    Vue.set(this.instance_list, index, instance);


    if (this.component_ctx) {
      this.component_ctx.$emit('instance_selected', instance, index)
    }
  }

  public on_click_edit_mode(event): void {
    if (!this.scene) {
      return
    }
    this.raycaster.setFromCamera(this.mouse, this.camera);

    // calculate objects intersecting the picking ray
    const intersects = this.raycaster.intersectObjects(this.scene.children.filter(obj => !this.excluded_objects_ray_caster.includes(obj.name)));

    if (intersects.length > 0) {
      console.log('INTERSEC INSTANCEE', intersects)
      let instance_object = intersects.find(elm => {
        if(elm.object.userData && elm.object.userData.instance_index != undefined){
          return true;
        }
        return false;
      });
      console.log('instance_object', instance_object)
      if(instance_object){
        let index = instance_object.object.userData.instance_index;
        let instance_to_select = this.instance_list[index];
        if (instance_to_select) {
          this.deselect_instance();
          this.select_instance(instance_to_select, index);
        }
      }



    }
  }

  public add_mesh_user_data_to_instance(instance, index) {

    instance.mesh.userData.instance_index = index;
    instance.mesh.userData.color = this.label_file.colour.hex;
  }

  public add_cube_to_instance_list(cuboid_mesh) {
    let new_instance = new Cuboid3DInstance(
      this,
      cuboid_mesh
    );
    new_instance.label_file = this.label_file;
    new_instance.label_file_id = this.label_file.id;
    new_instance.draw_on_scene()
    new_instance.update_spacial_data();
    this.instance_list.push(new_instance);

    let index = this.instance_list.length - 1;
    this.add_mesh_user_data_to_instance(new_instance, index)

    return new_instance
  }

  public start_render() {
    this.animate();
    // this.render();

  }


  public add_orbit_controls() {
    this.controls_orbit = new OrbitControls(this.camera, this.renderer.domElement)
    this.add_orbit_controls_events();
    this.controls_orbit.enableDamping = false; // an animation loop is required when either damping or auto-rotation are enabled
    this.controls_orbit.dampingFactor = 0.09;
    this.controls_orbit.screenSpacePanning = false;
    this.controls_orbit.enableRotate = true;
    this.controls_orbit.keyPanSpeed = this.controls_panning_speed
    this.controls_orbit.minDistance = 0;
    this.controls_orbit.maxDistance = 99999;

    // this.controls_orbit.maxPolarAngle = Math.PI/ 2;

    this.controls_orbit.keys = {
      LEFT: 'KeyA', //left arrow
      UP: 'KeyW', // up arrow
      RIGHT: 'KeyD', // right arrow
      BOTTOM: 'KeyS' // down arrow
    }

    this.controls_orbit.addEventListener('change', this.render.bind(this))
    this.controls_orbit.update();
  }

  public add_orbit_controls_events() {
    if(!this.controls_orbit){
      return
    }
    if(!this.controls_orbit._domElementKeyEvents){
      this.controls_orbit.listenToKeyEvents(window); // optional
    }

    this.controls_orbit.enabled = true
  }

  public remove_orbit_controls_events() {
    if(!this.controls_orbit){
      return
    }

    this.controls_orbit.enabled = false
  }

  public add_transform_controls() {
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

  public attach_transform_controls_to_mesh(mesh) {
    this.object_transform_controls.attach_to_mesh(mesh)

  }

  private detach_controls_from_mesh() {
    this.object_transform_controls.detach_controls();
  }

  public add_mesh_to_scene(mesh, center_camera_to_object = true) {
    if (!this.scene) {
      return
    }
    this.scene.add(mesh);


    if (center_camera_to_object) {
      this.center_camera_to_mesh(mesh)
    }
  }

  public center_camera_to_mesh(mesh, axis = 'x', offset = 1): void {
    // Read: https://discourse.threejs.org/t/camera-zoom-to-fit-object/936/6
    let camera = this.camera as THREE.PerspectiveCamera;
    let vFoV = camera.getEffectiveFOV();
    let hFoV = camera.fov * camera.aspect;

    let FoV = Math.min(vFoV, hFoV);
    let FoV2 = FoV / 2;

    let dir = new THREE.Vector3();
    camera.getWorldDirection(dir);

    let bb = mesh.geometry.boundingBox;
    let bs = mesh.geometry.boundingSphere;
    let bsWorld = bs.center.clone();
    mesh.localToWorld(bsWorld);

    let th = FoV2 * Math.PI / 180.0;
    let sina = Math.sin(th);
    let R = bs.radius;
    let FL = R / sina;

    let cameraDir = new THREE.Vector3();
    camera.getWorldDirection(cameraDir);

    let cameraOffs = cameraDir.clone();
    cameraOffs.multiplyScalar(-FL);
    let newCameraPos = bsWorld.clone().add(cameraOffs);

    camera.position.copy(newCameraPos);
    camera.lookAt(bsWorld);
    this.controls_orbit.target.copy(bsWorld);

    this.controls_orbit.update();


  }

}
