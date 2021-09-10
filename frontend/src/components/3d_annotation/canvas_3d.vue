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
        },
        radar_url: {
          default: "https://storage.googleapis.com/diffgram-sandbox/testing/radar_rear.pcd"
        },

      },
      data() {
        return {
          orbit_controls: null,
          renderer: null,
          scene_controller: null,
          camera: null,
        }
      },

      async mounted() {
        if ( WEBGL.isWebGLAvailable() ) {

          this.renderer = new THREE.WebGLRenderer();
          const scene = new THREE.Scene();
          document.getElementById('3d-container').appendChild( this.renderer.domElement );
          this.camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
          this.configure_orbit_controls(this.camera, this.renderer.domElement);

          this.scene_controller = new SceneController3D(scene, this.orbit_controls)

          this.point_cloud_mesh = await this.load_pcd();
          this.renderer.setSize( window.innerWidth, window.innerHeight );

          const axesHelper = new THREE.AxesHelper( 5 );
          scene.add( axesHelper );

          this.scene_controller.add_mesh_to_scene(this.point_cloud_mesh)

          this.camera.position.y = 10;
          window.addEventListener( 'resize', this.on_window_resize );
          let animate = () => {
            this.orbit_controls.update();
            requestAnimationFrame( animate );
            this.renderer.render( scene, this.camera );
          }
          animate();

        } else {
          const warning = WEBGL.getWebGLErrorMessage();
          alert('WebGL is not available on this machine.')

        }
      },
      computed: {

      },
      methods: {
        on_window_resize: function(){
          this.camera.aspect = window.innerWidth / window.innerHeight;
          this.camera.updateProjectionMatrix();

          this.renderer.setSize( window.innerWidth, window.innerHeight );
        },
        configure_orbit_controls: function(camera, dom_element){
          if(!this.$props.allow_navigation){
            return
          }
          this.orbit_controls = new OrbitControls(camera, dom_element)
          this.orbit_controls.listenToKeyEvents( window ); // optional
          this.orbit_controls.enableDamping = true; // an animation loop is required when either damping or auto-rotation are enabled
          this.orbit_controls.dampingFactor = 0.09;
          this.orbit_controls.screenSpacePanning = true;

          this.orbit_controls.minDistance = 0;
          this.orbit_controls.maxDistance = 99999;

          this.orbit_controls.maxPolarAngle = Math.PI/ 2;

          this.orbit_controls.keys = {
            LEFT: 'KeyA'  , //left arrow
            UP: 'KeyW', // up arrow
            RIGHT: 'KeyD', // right arrow
            BOTTOM: 'KeyS' // down arrow
          }

        },
        load_pcd: async function(){
          let file_loader_3d = new FileLoader3DPointClouds();
          this.point_cloud_mesh = await file_loader_3d.load_pcd_from_url(this.$props.pcd_url)
          return this.point_cloud_mesh

        }

      }
    }
  ) </script>
