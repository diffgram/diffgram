<template>
  <div :id="canvas_wrapper_id"
       style="position: relative"
       class="ma-auto"
       v-bind:style="{width: canvas_width, height: canvas_height}"
       @mousemove="mouse_move"
       @mousedown="mouse_down"
       @dblclick="double_click"
       @mouseup="mouse_up"
       @contextmenu="contextmenu">
    <canvas
      data-cy="canvas"
      v-canvas:cb="onRendered"
      :id="canvas_id"
      :canvas_transform="canvas_transform"
      :height="canvas_height_scaled"
      :width="canvas_width_scaled">
      <slot :ord="3" name="instance_drawer" :canvas_transform="canvas_transform"></slot>
      <v_bg
        :ord="1"
        :background="bg_color"
        ref="background"
        :image="image_bg"
        :refresh="refresh"
        :canvas_width="canvas_width"
        :canvas_height="canvas_height"
        :annotations_loading="annotations_loading"
        :auto_scale_bg="auto_scale_bg"
        @update_canvas="update_canvas"
      ></v_bg>

      <target_reticle target_type="canvas_cross"
                      v-if="editable && !show_context_menu"
                      :ord="2"
                      :x="mouse_position.x"
                      :y="mouse_position.y"
                      :mouse_position="mouse_position"
                      :height="canvas_height"
                      :width="canvas_width"
                      :show="show_target_reticle"
                      :target_colour="reticle_colour"
                      :canvas_element="canvas_element"
                      ref="reticle"
                      :text_color="text_color"
                      :target_text="this.instance.number"
                      :canvas_transform="canvas_transform">
      </target_reticle>

      <slot name="current_instance_drawer"></slot>

    </canvas>
    <slot name="context_menu" :mouse_position="mouse_position"></slot>
    <slot name="hover_menu" :mouse_position="mouse_position"></slot>
  </div>
</template>

<script>
  /*
  *
  * This component will become the base for using multiple canvases on the studio.
  * It abstracts the basic behaviour of a canvas for an image with its base components.
  *
  * */
  import Vue from "vue";
  import {KeypointInstance} from '../vue_canvas/instances/KeypointInstance';
  import v_bg from '../vue_canvas/v_bg';
  import target_reticle from '../vue_canvas/target_reticle';
  import {CanvasMouseTools} from '../vue_canvas/CanvasMouseTools';
  import axios from "axios";

  export default Vue.extend({
    name: "drawable_canvas",
    components: {
      target_reticle,
      v_bg
    },
    props: {
      canvas_wrapper_id:{
        default: 'canvas_wrapper'
      },
      project_string_id: {
        default: undefined
      },
      editable:{
        default: true
      },
      show_context_menu:{
        default: false
      },
      annotations_loading:{
        default: false
      },
      show_target_reticle: {
        default: true
      },
      auto_scale_bg:{
        default: false
      },
      text_color: {
        default: "#000000"
      },
      bg_color: {
        default: undefined
      },
      image_bg: {
        default: undefined
      },
      canvas_id: {
        default: 'my_canvas'
      },
      canvas_height: {
        default: 800
      },
      canvas_width: {
        default: 800
      },
      video_mode: {
        default: false
      },
      allow_zoom:{
        default: true
      },
      reticle_colour: {
        default: () => ({
          hex: '#ff0000',
          rgba: {
            r: 255,
            g: 0,
            b: 0,
            a: 1
          }
        })
      }
    },
    watch:{
      allow_zoom: function(newVal, oldVal){
        if(newVal && !oldVal){
          this.canvas_wrapper.addEventListener('wheel', this.zoom_wheel_scroll_canvas_transform_update)
        }
        else if(!newVal && oldVal){
          this.canvas_wrapper.removeEventListener('wheel', this.zoom_wheel_scroll_canvas_transform_update);
        }

      },
      mouse_computed(newval, oldval){
        this.mouse_down_delta_event.x = parseInt(newval.delta_x - oldval.delta_x)
        this.mouse_down_delta_event.y = parseInt(newval.delta_y - oldval.delta_y)
      },
      image_bg: function(){
        if(!this.$props.video_mode){
          this.canvas_element.width+=0;
          this.update_window_size_from_listener();
          this.update_canvas();
        }
        else{
          this.canvas_element.width+=0;

          this.update_window_size_from_listener();
          this.update_canvas();
        }
        this.$emit('refresh')
      }
    },
    data: function () {
      return {
        mouse_down_position: {
          request_time: null,
          x: 0,
          y: 0,
          raw: {
            x: 0,
            y: 0
          }
        },
        mouse_down_delta_event: { x : 0, y : 0},
        mouse_position: {
          raw: {
            x: 0,
            y: 0
          },
          x: 150,
          y: 150
        },
        canvas_translate: {
          x: 0,
          y: 0
        },
        zoom_canvas: 1,
        canvas_scale_local: 1,
        canvas_element: null,
        canvas_scale_global: 1,
        canvas_scale_global_y: 1,
        canvas_scale_global_x: 1,

        canvas_mouse_tools: undefined,
        refresh: undefined,
        window_width_from_listener: undefined,
        window_height_from_listener: undefined,
        canvas_ctx: undefined,
        instance_type: 'keypoints',

        instance: {},

      }
    },
    async mounted() {
      this.loading = true;
      this.canvas_element =  document.getElementById(this.$props.canvas_id);
      this.canvas_element.onselectstart = function () { return false; }
      await this.$nextTick();
      this.canvas_mouse_tools = new CanvasMouseTools(
        this.mouse_position,
        this.canvas_translate,
        this.canvas_element,
        this.canvas_scale_global
      )
      this.canvas_wrapper = document.getElementById(this.$props.canvas_wrapper_id)
      if(this.$props.allow_zoom){
        this.canvas_wrapper.addEventListener('wheel', this.zoom_wheel_scroll_canvas_transform_update)
      }

      window.addEventListener('resize', this.update_window_size_from_listener)
      this.update_window_size_from_listener();

      this.loading = false;
      this.canvas_ctx = this.canvas_element.getContext('2d');

      this.update_canvas();

    },

    beforeDestroy() {
      if(this.$props.allow_zoom){
        this.canvas_wrapper.removeEventListener('wheel', this.zoom_wheel_scroll_canvas_transform_update);
      }
      window.removeEventListener('resize', this.update_window_size_from_listener)
    },
    methods: {

      update_window_size_from_listener: async function(){
        if(!this.$props.image_bg){
          return
        }
        let width_scaled = this.$props.canvas_width / this.$props.image_bg.width;
        let height_scaled = this.$props.canvas_height / this.$props.image_bg.height;
        // careful to do the scale first, so we do the min of scaled values
        let lowest_size = Math.min(height_scaled, width_scaled)

        let new_size = Math.round(lowest_size * 100) / 100
        if(isFinite(width_scaled)){
          this.canvas_scale_global_x = width_scaled;
        }
        if(isFinite(height_scaled)){
          this.canvas_scale_global_y = height_scaled;
        }
        await this.$nextTick();
      },
      zoom_wheel_scroll_canvas_transform_update: function (event) {
        this.canvas_translate = this.canvas_mouse_tools.zoom_wheel(event);
        this.update_canvas();
      },
      mouse_transform: function (event, mouse_position) {
        return this.canvas_mouse_tools.mouse_transform(event, mouse_position, this.canvas_element, () => {}, this.canvas_transform)
      },
      mouse_move: function (event) {
        this.mouse_position = this.mouse_transform(event, this.mouse_position);
        this.$emit('mousemove', event)

      },
      mouse_down: function (event) {
        this.$store.commit('mouse_state_down')
        this.$emit('mousedown', event)
        this.mouse_down_position = this.mouse_transform(event, this.mouse_down_position);
        this.mouse_down_position.request_time = Date.now()
      },
      double_click: function (event) {
        this.$emit('dblclick', event)
      },
      mouse_up: function (event) {
        this.$store.commit('mouse_state_up')
        this.$emit('mouseup', event)
      },
      contextmenu: function (event) {
        this.$emit('contextmenu', event)
      },
      onRendered: function (ctx) {
        this.canvas_ctx = ctx;


      },
      update_canvas: function(){
        this.refresh = new Date();
        this.canvas_element_ctx = this.canvas_element.getContext('2d');

        this.$forceUpdate();
      },
      zoom_in: function() {
        this.canvas_mouse_tools.zoom_in()
        this.update_canvas()
      },
      zoom_out: function() {
        this.canvas_mouse_tools.zoom_out()
        this.update_canvas()
      }


    },
    computed: {


      canvas_width_scaled: function () {
        return this.canvas_width  * this.canvas_scale_global
      },

      canvas_height_scaled: function () {
        return this.canvas_height * this.canvas_scale_global
      },

      mouse_computed: function () {
        if (this.$store.state.annotation_state.mouse_down == false) {
          return {
            delta_x : 0,
            delta_y : 0
          }
        }
        let delta_x = this.mouse_position.x - this.mouse_down_position.x
        let delta_y = this.mouse_position.y - this.mouse_down_position.y
        delta_x = parseInt(delta_x)
        delta_y = parseInt(delta_y)
        return {
          delta_x : delta_x,
          delta_y : delta_y
        }
      },

      canvas_transform: function () {
        return {
          'canvas_scale_global_x': this.canvas_scale_global_x,
          'canvas_scale_global_y': this.canvas_scale_global_y,
          'canvas_scale_global': this.canvas_scale_global,
          'canvas_scale_local': this.canvas_scale_local,
          'canvas_scale_combined': this.canvas_scale_local * this.canvas_scale_global,
          'translate': this.canvas_translate,
          'translate_previous': this.canvas_translate,
          'zoom_canvas': this.zoom_canvas
        }
      },
    }

  })
</script>

<style scoped>

</style>
