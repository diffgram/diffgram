import * as THREE from 'three';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls';
import SceneController3D from "./SceneController3D";

export default class ObjectTransformControls {
  controls_transform: TransformControls;
  scene_controller: SceneController3D;

  public constructor(camera, scene_controller, domeElement, scene, render_function, drag_function, layer_number) {
    this.controls_transform = new TransformControls( camera, domeElement );
    this.controls_transform.addEventListener( 'change', render_function );
    this.controls_transform.addEventListener( 'dragging-changed', drag_function);
    this.scene_controller = scene_controller;
    console.log('ObjectTransformControls', this.controls_transform, layer_number)
    let gizmo = this.controls_transform._gizmo.gizmo;
    let picker = this.controls_transform._gizmo.picker;
    let helper = this.controls_transform._gizmo.helper;

    gizmo['translate'].traverse( function( child ) { child.layers.set( 1 ) });
    gizmo['rotate'].traverse( function( child ) { child.layers.set( 1 ) });
    gizmo['scale'].traverse( function( child ) { child.layers.set( 1 ) });


    picker['translate'].layers.set(layer_number);
    picker['rotate'].layers.set(layer_number);
    picker['scale'].layers.set(layer_number);

    helper['translate'].layers.set(layer_number);
    helper['rotate'].layers.set(layer_number);
    helper['scale'].layers.set(layer_number);



    this.controls_transform.addEventListener('objectChange', this.on_mesh_changed.bind(this));
    scene.add(this.controls_transform)
  }

  private on_mesh_changed(event){
    let instance_index= event.target.object.userData.instance_index;
    let instance = this.scene_controller.instance_list[instance_index];
    if(instance.helper_lines){
      instance.helper_lines.position.copy(instance.mesh.position)
      instance.helper_lines.rotation.copy(instance.mesh.rotation)
      instance.helper_lines.scale.copy(instance.mesh.scale)
    }
    instance.update_spacial_data();
    this.scene_controller.component_ctx.$emit('instance_updated', instance)
  }

  private on_key_down(event){
    let currentCamera = this.controls_transform.camera;
    let control = this.controls_transform;

    switch ( event.keyCode ) {

      case 81: // Q
        control.setSpace( control.space === 'local' ? 'world' : 'local' );
        break;

      case 16: // Shift
        control.setTranslationSnap( 100 );
        control.setRotationSnap( THREE.MathUtils.degToRad( 15 ) );
        control.setScaleSnap( 0.25 );
        break;

      case 84: // T
        if(control.mode === 'translate'){
          control.setMode( 'scale' );
        }
        else if(control.mode === 'scale'){
          control.setMode( 'rotate' );
        }
        else{
          control.setMode( 'translate' );
        }

        break;
      case 187:
      case 107: // +, =, num+
        control.setSize( control.size + 0.1 );
        break;

      case 189:
      case 109: // -, _, num-
        control.setSize( Math.max( control.size - 0.1, 0.1 ) );
        break;

      case 88: // X
        control.showX = ! control.showX;
        break;

      case 89: // Y
        control.showY = ! control.showY;
        break;

      case 90: // Z
        control.showZ = ! control.showZ;
        break;

      case 32: // Spacebar
        control.enabled = ! control.enabled;
        break;


      case 27: // ESC
        if(this.scene_controller.selected_instance){
          this.scene_controller.deselect_instance()
        }
        this.controls_transform.detach();

        break;

    }
  }
  private add_hotkeys_for_transform_controls(){
    window.addEventListener( 'keydown', this.on_key_down.bind(this));

  }

  public detach_controls(){
    if(this.controls_transform){
      this.controls_transform.detach()

    }
  }
  public attach_to_mesh(mesh){
    this.controls_transform.attach(mesh);
    this.add_hotkeys_for_transform_controls();
  }


}
