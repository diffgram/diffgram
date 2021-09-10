import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { Camera } from 'three/src/cameras/Camera';
import { Euler } from 'three/src/math/Euler';

const _PI_2 = Math.PI / 2;

export default class Diffgram3DOrbitControls extends OrbitControls{
  public camera: Camera;
  private euler: Euler;
  private changeEvent: Object;

  public constructor(camera, domElement ) {
    super(camera, domElement );
    this.camera = camera
    this.euler = new Euler( 0, 0, 0, 'YXZ' );
    this.changeEvent = { type: 'change' };
    this.domElement.addEventListener( 'pointerdown', onPointerDown );
  }
  public on_pointer_down(){
    if ( this.enabled === false ) return;

    if ( this.pointers.length === 0 ) {

      this.domElement.setPointerCapture( event.pointerId );

      this.domElement.addEventListener( 'pointermove', onPointerMove );
      this.domElement.addEventListener( 'pointerup', onPointerUp );

    }

    this.addPointer( event );

    if ( event.pointerType === 'touch' ) {

      this.onTouchStart( event );

    } else {

      this.onMouseDown( event );

    }

  }

  public rotate_based_on_mouse(event){

    const movementX = event.movementX || event.mozMovementX || event.webkitMovementX || 0;
    const movementY = event.movementY || event.mozMovementY || event.webkitMovementY || 0;

    this.euler.setFromQuaternion( this.camera.quaternion );

    this.euler.y -= movementX * 0.002;
    this.euler.x -= movementY * 0.002;

    this.euler.x = Math.max( _PI_2 - this.maxPolarAngle, Math.min( _PI_2 - this.minPolarAngle, this.x ) );

    this.camera.quaternion.setFromEuler( this.euler );

    this.dispatchEvent( this.changeEvent );
  }

  public onPointerUp = function( event ) {

    if ( this.enabled === false ) return;

    if ( event.pointerType === 'touch' ) {

      this.onTouchEnd();

    } else {

      this.onMouseUp( event );

    }
    this.removePointer( event );

    if ( this.pointers.length === 0 ) {

      this.domElement.releasePointerCapture( event.pointerId );

      this.domElement.removeEventListener( 'pointermove', onPointerMove );
      this.domElement.removeEventListener( 'pointerup', onPointerUp );

    }

  }
}
