import * as THREE from 'three';
import {PCDLoader} from 'three/examples/jsm/loaders/PCDLoader';

export default class FileLoader3DPointClouds {

  pcd_loading_status: string = 'pending';

  public constructor() {

  }

  public async load_pcd_from_url(url) {
    return new Promise((resolve, reject) => {
      let pcd_loader = new PCDLoader();
      pcd_loader.load(url,
        (mesh) => {
          console.log('SUCCESS', mesh)
          mesh.material.color.set('white');
          resolve(mesh)
        },
        (xhr) => {
          console.log((xhr.loaded / xhr.total * 100) + '% loaded');
          this.pcd_loading_status = 'in_progress'
        },
        (error) => {
          reject(error);
        }
      );
    })
  }
}
