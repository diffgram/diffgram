<template>
  <div id="3d-container">

  </div>

</template>

<script lang="ts">
  import {WEBGL} from "./WebGL";
  import Vue from "vue";
  import * as THREE from "three";
  import SceneController3D from './SceneController3D';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
  import { TransformControls } from 'three/examples/jsm/controls/TransformControls';
  import Cuboid3DInstance from "../vue_canvas/instances/Cuboid3DInstance";
  import FileLoader3DPointClouds from './FileLoader3DPointClouds';

  export default Vue.extend({
      name: 'canvas_3d',
      components: {

      },
      props: {
        with_keyboard_controls: {
          default: false
        },
        allow_navigation:{
          default: false
        },
        pcd_url: {
          default: "https://storage.googleapis.com/diffgram-sandbox/testing/lidar_ascii_v5.pcd"
          // default: "https://diffgrampublic1.s3.amazonaws.com/Zaghetto.pcd"
        },
        radar_url: {
          default: "https://storage.googleapis.com/diffgram-sandbox/testing/radar_rear.pcd"
        },

      },
      data() {
        return {
          controls_transform: null,
          controls_orbit: null,
          renderer: null,
          scene_controller: null,
          camera: null,
        }
      },

      async mounted() {
        if ( WEBGL.isWebGLAvailable() ) {

          this.renderer = new THREE.WebGLRenderer();
          this.renderer.setPixelRatio( window.devicePixelRatio );
          this.renderer.setSize( window.innerWidth, window.innerHeight );

          const scene = new THREE.Scene();
          document.getElementById('3d-container').appendChild( this.renderer.domElement );
          this.camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );


          this.scene_controller = new SceneController3D(scene, this.camera, this.renderer)

          this.scene_controller.attach_mouse_events();

          this.configure_controls();

          this.point_cloud_mesh = await this.load_pcd();

          this.scene_controller.add_mesh_to_scene(this.point_cloud_mesh)

          this.camera.position.y = 10;
          window.addEventListener( 'resize', this.on_window_resize );
          this.scene_controller.start_render();
          let cuboid = new Cuboid3DInstance(this.scene_controller, 0, 30);
          cuboid.draw_on_scene();
          if(cuboid.mesh){
            this.scene_controller.attach_transform_controls_to_mesh(cuboid.mesh)
          }

        } else {
          const warning = WEBGL.getWebGLErrorMessage();
          alert('WebGL is not available on this machine.')

        }
      },
      beforeDestroy() {
        this.scene_controller.detach_mouse_events();
      },
    computed: {

      },
      methods: {
        on_window_resize: function(){
          this.camera.aspect = window.innerWidth / window.innerHeight;
          this.camera.updateProjectionMatrix();

          this.renderer.setSize( window.innerWidth, window.innerHeight );
        },
        configure_controls: function(){
          if(!this.$props.allow_navigation){
            return
          }

          this.scene_controller.add_orbit_controls();
          this.scene_controller.add_transform_controls();


        },
        load_pcd: async function(){
          let file_loader_3d = new FileLoader3DPointClouds();
          this.point_cloud_mesh = await file_loader_3d.load_pcd_from_url(this.$props.pcd_url)
          return this.point_cloud_mesh

        }

      }
    }
  ) </script>
