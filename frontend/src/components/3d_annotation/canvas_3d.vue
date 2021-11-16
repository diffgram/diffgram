<template>
  <div v-if="point_cloud_mesh" :id="container_id" :style="{width: `${width}px`, height: `${height}px`}" class="ma-0">

  </div>


</template>

<script lang="ts">
  import {WEBGL} from "./WebGL";
  import Vue from "vue";
  import * as THREE from "three";
  import SceneController3D from './SceneController3D';
  import SceneControllerOrtographicView from './SceneControllerOrtographicView';

  export default Vue.extend({
      name: 'canvas_3d',
      components: {},
      props: {
        point_cloud_mesh:{
          default: null,
          type: Object
        },
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
          default: null
          // default: "https://diffgrampublic1.s3.amazonaws.com/Zaghetto.pcd"
        },
        radar_url: {
          default: null
        },
        instance_list: {
          default: []
        },
        container_id: {
          default: '3d-container'
        },
        draw_mode: {
          default: false
        },
        zoom_speed:{
          default: 1
        },
        pan_speed:{
          default: 1
        }

      },
      data() {
        return {
          controls_transform: null,
          percentage: 0,
          controls_orbit: null,
          loading_pcd: true,
          renderer: null,
          container: null,
          scene_controller: null,
          camera: null,
        }
      },

      async mounted() {

        this.load_canvas();

      },
      beforeDestroy() {
        if (this.scene_controller) {
          this.destroy_canvas();
        }

      },
      computed: {

      },
      watch:{
        zoom_speed: function(new_val, old_val){
          this.update_zoom_speed(new_val)
        },
        pan_speed: function(new_val, old_val){
          this.update_pan_speed(new_val)
        },
        width: function(){
          this.update_camera_aspect_ratio();
        },
        height: function(){
          this.update_camera_aspect_ratio();
        }
      },
      methods: {
        load_canvas: async function(){
          if (WEBGL.isWebGLAvailable()) {
            if (this.$props.create_new_scene) {

              await this.setup_scene()
            }
          } else {
            const warning = WEBGL.getWebGLErrorMessage();
            alert('WebGL is not available on this machine.')

          }
        },
        destroy_canvas: function(){
          if(this.scene_controller){
            // Clear all elements from the scene
            this.scene_controller.detach_mouse_events();
            this.scene_controller.scene.remove(this.point_cloud_mesh);
            this.point_cloud_mesh.geometry.dispose();
            this.point_cloud_mesh.material.dispose();

            this.scene_controller.clear_all();

            let container = document.getElementById(this.$props.container_id)
            if(container && this.renderer){
              if(container.contains(this.renderer.domElement)){
                document.getElementById(this.$props.container_id).removeChild(this.renderer.domElement);
              }

            }

            delete this.renderer;
            delete this.scene_controller.scene;

            this.renderer = undefined;

            this.scene_controller = undefined;
          }
        },
        update_pan_speed: function(){
          this.scene_controller.controls_orbit.panSpeed = this.$props.pan_speed;
          this.scene_controller.controls_orbit.update();
        },
        update_zoom_speed: function(){
          this.scene_controller.controls_orbit.zoomSpeed = this.$props.zoom_speed;
          this.scene_controller.controls_orbit.update();
        },
        setup_ortographic_scene_controller: function (scene) {
          this.camera = new THREE.OrthographicCamera(
            -20,
            20,
            -20,
            20,
            0.1,
            1000);
          this.scene_controller = new SceneControllerOrtographicView(scene, this.camera, this.renderer, this.container, this, this.$props.instance_list)
          this.scene_controller.attach_mouse_events();

          this.scene_controller.set_draw_mode(this.$props.draw_mode);
          this.scene_controller.set_current_label_file(this.$props.current_label_file);

        },
        setup_perspective_scene_controller: function (scene) {
          this.camera = new THREE.PerspectiveCamera(75, this.container.clientWidth / this.container.clientHeight, 0.1, 1000);
          this.scene_controller = new SceneController3D(scene, this.camera, this.renderer, this.container, this, this.$props.instance_list)
          this.scene_controller.attach_mouse_events();
          this.scene_controller.set_draw_mode(this.$props.draw_mode);
          this.scene_controller.set_current_label_file(this.$props.current_label_file);
        },
        create_renderer: function(){
          this.renderer = new THREE.WebGLRenderer();

          this.renderer.setPixelRatio(window.devicePixelRatio);

          this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        },
        setup_scene: async function (scene = undefined,) {

          this.container = document.getElementById(this.$props.container_id)


          if(this.container.clientWidth === 0 || this.container.clientHeight === 0){
            return
          }

          if(!this.renderer){
            this.create_renderer();
          }

          window.addEventListener( 'resize', this.on_window_resize );
          if (!scene) {
            scene = new THREE.Scene();
            // scene.background = new THREE.Color('blue')
          }
          document.getElementById(this.$props.container_id).appendChild(this.renderer.domElement);

          // Disable selecting text when double clicking inside canvas
          // see: https://stackoverflow.com/questions/3684285/how-to-prevent-text-select-outside-html5-canvas-on-double-click
          this.renderer.domElement.onselectstart = function () { return false; }
          if (this.$props.camera_type === 'perspective') {
            this.setup_perspective_scene_controller(scene);
            this.configure_controls();
          } else if (this.$props.camera_type === 'ortographic') {
            this.setup_ortographic_scene_controller(scene)
          }

          this.scene_controller.add_mesh_to_scene(this.point_cloud_mesh)

          this.camera.position.y = 10;

          this.add_instance_list_to_scene();

          this.scene_controller.start_render();

          this.$emit('scene_ready', this.scene_controller)
        },
        set_current_label_file: function (label_file) {
          if(!this.scene_controller){
            return
          }
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
        update_camera_aspect_ratio: function(){
          if(!this.camera){
            return
          }
          let w = this.container.clientWidth
          let h = this.container.clientHeight
          this.camera.aspect = w / h;
          this.camera.updateProjectionMatrix();
          this.renderer.setSize(w, h);
        },
        on_window_resize: function () {
          this.update_camera_aspect_ratio();
        },
        configure_controls: function () {
          if (!this.$props.allow_navigation) {
            return
          }

          this.scene_controller.add_orbit_controls();
          this.scene_controller.controls_orbit.zoomSpeed = this.$props.zoom_speed;
          this.scene_controller.controls_orbit.panSpeed = this.$props.pan_speed;
          this.scene_controller.add_transform_controls();


        },


      }
    }
  ) </script>
