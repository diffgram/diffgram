import * as THREE from 'three';
// import {PCDLoader} from 'three/examples/jsm/loaders/PCDLoader';
import PCDLoader from "./PCDLoader"; // Importing the local PCDLoader
import Vue from "vue/types/vue";

export default class FileLoader3DPointClouds {
  // Declaring the component context property
  component_ctx: {loading_pcd: boolean, percentage: number};
  // Declaring the status of PCD loading
  pcd_loading_status: string = 'pending';
  // Declaring the PCD loader instance
  public pcd_loader: PCDLoader;

  // Constructor to initialize the component context and PCD loader
  public constructor(component_ctx: {loading_pcd: boolean, percentage: number}) {
    this.component_ctx = component_ctx;
    this.pcd_loader = new PCDLoader();
  }

  // Method to load PCD file from a URL
  public async load_pcd_from_url(url) {
    return new Promise((resolve, reject) => {
      let pcd_loader = this.pcd_loader;
      // Using the PCD loader to load the PCD file
      pcd_loader.load(url,
        (mesh) => {
          // Setting the material color and name of the loaded mesh
          let material = mesh.material as THREE.MeshBasicMaterial;
          material.color.set('white');
          mesh.name = 'point_cloud';
          // Updating the component context to indicate the PCD loading is done
          this.component_ctx.loading_pcd = false;
          // mesh.geometry.center();
          // mesh.geometry.rotateX( Math.PI );
          resolve(mesh);
        },
        // Callback for progress updates
        (xhr) => {
          let percentage = (xhr.loaded / xhr.total * 100);
          this.pcd_loading_status = 'in_progress';
          if(this.component_ctx){
            this.component_ctx.loading_pcd = true;
            this.component_ctx.percentage = percentage * 100;
          }
        },
        // Callback for errors
        (error) => {
          reject(error);
        }
      );
    })
  }
}

