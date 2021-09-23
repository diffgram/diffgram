<template>
  <div :id="container_id" :style="{width: width, height: height}">

  </div>

</template>

<script lang="ts">
  import {WEBGL} from "./WebGL";
  import Vue from "vue";
  import * as THREE from "three";
  import SceneController3D from './SceneController3D';
  import SceneControllerOrtographicView from './SceneControllerOrtographicView';
  import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls';
  import {TransformControls} from 'three/examples/jsm/controls/TransformControls';
  import Cuboid3DInstance from "../vue_canvas/instances/Cuboid3DInstance";
  import FileLoader3DPointClouds from './FileLoader3DPointClouds';

  export default Vue.extend({
      name: 'canvas_3d',
      components: {},
      props: {
        width: {
          default: 'auto'
        },
        height: {
          default: 'auto'
        },
        camera_type: {
          default: 'perspective'
        },
        create_new_scene: {
          default: true
        },
        with_keyboard_controls: {
          default: false
        },
        current_label_file: {
          default: false
        },
        allow_navigation: {
          default: false
        },
        pcd_url: {
          default: "https://storage.googleapis.com/diffgram-sandbox/testing/lidar_ascii_v5.pcd"
          // default: "https://diffgrampublic1.s3.amazonaws.com/Zaghetto.pcd"
        },
        radar_url: {
          default: "https://storage.googleapis.com/diffgram-sandbox/testing/radar_rear.pcd"
        },
        instance_list: {
          default: []
        },
        container_id: {
          default: '3d-container'
        },
        draw_mode: {
          default: false
        }

      },
      data() {
        return {
          controls_transform: null,
          controls_orbit: null,
          renderer: null,
          container: null,
          scene_controller: null,
          camera: null,
        }
      },

      async mounted() {
        if (WEBGL.isWebGLAvailable()) {
          if (this.$props.create_new_scene) {
            await this.setup_scene_controls()
          }


        } else {
          const warning = WEBGL.getWebGLErrorMessage();
          alert('WebGL is not available on this machine.')

        }
      },
      beforeDestroy() {
        if (this.scene_controller) {
          this.scene_controller.detach_mouse_events();
        }

      },
      computed: {},
      methods: {
        setup_ortographic_scene_controller: function (scene) {
          this.camera = new THREE.OrthographicCamera(
            -20,
            20,
            -20,
            20,
            0.1,
            1000);
          this.scene_controller = new SceneControllerOrtographicView(scene, this.camera, this.renderer, this.container, this)
          this.scene_controller.attach_mouse_events();
          this.scene_controller.set_draw_mode(this.$props.draw_mode)
          this.scene_controller.set_current_label_file(this.$props.current_label_file)
        },
        setup_perspective_scene_controller: function (scene) {
          this.camera = new THREE.PerspectiveCamera(75, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
          this.scene_controller = new SceneController3D(scene, this.camera, this.renderer, this.container, this)
          this.scene_controller.attach_mouse_events();
          this.scene_controller.set_draw_mode(this.$props.draw_mode)
          this.scene_controller.set_current_label_file(this.$props.current_label_file)
        },
        setup_scene_controls: async function (scene = undefined,) {
          this.container = document.getElementById(this.$props.container_id)
          console.log('SETTINGS SCENETE', this.container.clientWidth, this.container.clientHeight, this.$props.width, 'qq');
          if(this.container.clientWidth === 0 || this.container.clientHeight === 0){
            return
          }
          this.renderer = new THREE.WebGLRenderer();

          this.renderer.setPixelRatio(window.devicePixelRatio);

          this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);

          if (!scene) {
            scene = new THREE.Scene();
          }
          document.getElementById(this.$props.container_id).appendChild(this.renderer.domElement);
          if (this.$props.camera_type === 'perspective') {
            this.setup_perspective_scene_controller(scene);
          } else if (this.$props.camera_type === 'ortographic') {
            this.setup_ortographic_scene_controller(scene)
          }
          this.configure_controls();

          this.point_cloud_mesh = await this.load_pcd();

          this.scene_controller.add_mesh_to_scene(this.point_cloud_mesh)

          this.camera.position.y = 10;
          window.addEventListener('resize', this.on_window_resize);

          this.add_instance_list_to_scene();

          this.scene_controller.start_render();
        },
        set_current_label_file: function (label_file) {
          this.scene_controller.set_current_label_file(label_file)
        },
        set_draw_mode: function (draw_mode) {
          this.scene_controller.set_draw_mode(draw_mode);
        },
        add_instance_list_to_scene: function () {
          for (const instance of this.$props.instance_list) {
            instance.draw_on_scene();
          }
        },
        on_window_resize: function () {
          let w = this.container.clientWidth
          let h = this.container.clientHeight
          this.camera.aspect = w / h;
          this.camera.updateProjectionMatrix();

          this.renderer.setSize(w, h);
        },
        configure_controls: function () {
          if (!this.$props.allow_navigation) {
            return
          }

          this.scene_controller.add_orbit_controls();
          this.scene_controller.add_transform_controls();


        },
        load_pcd: async function () {
          let file_loader_3d = new FileLoader3DPointClouds();
          this.point_cloud_mesh = await file_loader_3d.load_pcd_from_url(this.$props.pcd_url)
          return this.point_cloud_mesh

        }

      }
    }
  ) </script>
