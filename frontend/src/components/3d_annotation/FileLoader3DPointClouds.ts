import * as THREE from 'three';
import {PCDLoader} from 'three/examples/jsm/loaders/PCDLoader';
import Vue from "vue/types/vue";

export default class FileLoader3DPointClouds {
  component_ctx: Vue;
  pcd_loading_status: string = 'pending';

  public constructor(component_ctx) {
    this.component_ctx = component_ctx;
  }

  public async load_pcd_from_url(url) {
    return new Promise((resolve, reject) => {
      let pcd_loader = new PCDLoader();
      pcd_loader.load(url,
        (mesh) => {
          mesh.material.color.set('white');
          mesh.name = 'point_cloud'
          this.component_ctx.loading_pcd = false;
          resolve(mesh)
        },
        (xhr) => {
          let percentage = (xhr.loaded / xhr.total * 100);
          this.pcd_loading_status = 'in_progress'
          if(this.component_ctx){
            this.component_ctx.loading_pcd = true;
            this.component_ctx.percentage = percentage * 100;
          }
        },
        (error) => {
          reject(error);
        }
      );
    })
  }
}
