import * as THREE from 'three';
import {Instance} from './Instance'
import SceneController3D from "../../3d_annotation/SceneController3D";

export default class Cuboid3DInstance extends Instance {

  scene_controller_3d: SceneController3D;

  public constructor(scene_controller_3d: SceneController3D, x, y) {
    super();
    this.scene_controller_3d = scene_controller_3d;
    this.center_x = x;
    this.center_y = y;
  }

  public draw_on_scene(){
    let render = this.scene_controller_3d.render;
    let renderer = this.scene_controller_3d.renderer;

    const texture = new THREE.TextureLoader().load( 'textures/crate.gif', render.bind(this) );
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();

    const geometry = new THREE.BoxGeometry( 2, 2, 2 );
    const material = new THREE.MeshStandardMaterial({
      color: new THREE.Color('red'),
      opacity: 0.5,
      transparent: true,
    });

    const cube = new THREE.Mesh(geometry, material);
    const mesh = new THREE.Mesh( geometry, material );
    alert('adding cube')
    this.scene_controller_3d.add_mesh_to_scene(mesh, false)
  }


}
