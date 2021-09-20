import * as THREE from 'three';
import { TransformControls } from 'three/examples/jsm/controls/TransformControls';

export default class ObjectTransformControls {
  controls_transform: TransformControls;

  public constructor(camera, domeElement, scene, render_function, drag_function) {
    this.controls_transform = new TransformControls( camera, domeElement );
    this.controls_transform.addEventListener( 'change', render_function );
    this.controls_transform.addEventListener( 'dragging-changed', drag_function);
    scene.add(this.controls_transform)
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

      case 84: // W
        if(control.mode === 'translate'){
          control.setMode( 'rotate' );
        }
        else if(control.mode === 'rotate'){
          control.setMode( 'scale' );
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

    }
  }
  private add_hotkeys_for_transform_controls(){
    window.addEventListener( 'keydown', this.on_key_down.bind(this));

  }

  public attach_to_mesh(mesh){
    this.controls_transform.attach(mesh);
    this.add_hotkeys_for_transform_controls();
  }


}
