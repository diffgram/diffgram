<template>
  <v-dialog v-model="is_open" width="700px" height="700px" :persistent="true" :no-click-animation="true"
            content-class="dialog-instance-template">
    <v-card elevation="0" class="pa-4">
      <v-card-title>
        Create KeyPoints Template:
      </v-card-title>
      <v-card-text>
        <v-container class="flex flex-column">
          <v-text-field data-cy="instance_template_name_text_field"
                        label="Name"
                        v-model="name"></v-text-field>
          <instance_template_creation_toolbar
            ref="instance_template_creation_toolbar"
            @draw_mode_update="update_draw_mode_on_instances"
            @set_background="set_background"
            :project_string_id="project_string_id"
            @zoom_in="zoom_in"
            @zoom_out="zoom_out"
          >

          </instance_template_creation_toolbar>
          <v_error_multiple :error="error">
          </v_error_multiple>
          <drawable_canvas
            @mousemove="mouse_move"
            @mousedown="mouse_down"
            @dblclick="double_click"
            @mouseup="mouse_up"
            @contextmenu="contextmenu"
            :canvas_width="canvas_width"
            :canvas_height="canvas_height"
            :image_bg="image_bg"
            :annotations_loading="false"
            :bg_color="bg_color"
            :auto_scale_bg="true"
            ref="instance_template_canvas"
          >
            <instance_drawer
              slot="instance_drawer"
              @instance_hover_update="instance_hover_update($event[0], $event[1])"
              :instance_list="instance_list"
            ></instance_drawer>
          </drawable_canvas>
        </v-container>
      </v-card-text>
      <v-card-actions class="flex justify-end pa-0">
        <v-btn color="error" text @click="is_open = false"><v-icon>mdi-close</v-icon>Discard Changes</v-btn>
        <v-btn color="success" data-cy="save_instance_template_button" text @click="save_instance_template">
          <v-icon>mdi-content-save</v-icon>
          Save Instance Template</v-btn>
      </v-card-actions>

    </v-card>
  </v-dialog>
</template>

<script>
  import Vue from "vue";
  import {KeypointInstance} from '../vue_canvas/instances/KeypointInstance';
  import {InstanceTemplateCreationInteractionGenerator} from '../vue_canvas/interactions/InstanceTemplateCreationInteractionGenerator';
  import drawable_canvas from '../vue_canvas/drawable_canvas';
  import axios from 'axios';
  import instance_drawer from '../vue_canvas/instance_drawer';
  import instance_template_creation_toolbar from './instance_template_creation_toolbar'
  import {InstanceContext} from "../vue_canvas/instances/InstanceContext";

  export default Vue.extend({
    name: "instance_template_creation_dialog",
    props: {
      project_string_id: undefined,
      instance_template: undefined,
    },
    components: {
      drawable_canvas: drawable_canvas,
      instance_drawer: instance_drawer,
      instance_template_creation_toolbar: instance_template_creation_toolbar,
    },
    data: function () {
      return {
        instance_type: 'keypoints',
        instance_context: new InstanceContext(),
        draw_mode: true ,
        lock_point_hover_change: false ,
        instance: undefined,
        error: {},
        bg_color: 'grey',
        image_bg: undefined,
        canvas_wrapper: undefined,
        canvas_width: 600,
        canvas_height: 600,
        is_open: false,
        name: undefined,
        label_settings: {
          show_occluded_keypoints: true,
          show_left_right_arrows: true
        }
      }
    },
    mounted() {



    },

    methods: {

      open: async function () {
        this.is_open = true;
        await this.$nextTick();
        let nodes = [];
        let edges = [];
        this.instance = new KeypointInstance(
          this.$refs.instance_template_canvas.mouse_position,
          this.$refs.instance_template_canvas.canvas_ctx,
          this.instance_context,
          () => {},
          () => {},
          () => {},
          this.$refs.instance_template_canvas.mouse_down_delta_event,
          this.label_settings
        );


        // Set this to allow the creation of new nodes and edges.
        this.instance.template_creation_mode = true;

        if(this.$props.instance_template){
          for(let i = 0; i < this.instance_template.instance_list.length; i++){
            nodes = this.$props.instance_template.instance_list[i].nodes;
            edges = this.$props.instance_template.instance_list[i].edges;
            this.name = this.$props.instance_template.name;
            this.instance.nodes = nodes;
            this.instance.edges = edges;
            this.instance.id = this.$props.instance_template.instance_list[i].id
          }

        }
        window.addEventListener('keydown', this.key_down_handler);

        },
      zoom_in: function () {
        this.$refs.instance_template_canvas.zoom_in();
      },
      zoom_out: function () {
        this.$refs.instance_template_canvas.zoom_out();
      },
      set_background: function (image) {
        this.image_bg = image;
        this.bg_color = undefined
        let canvas = this.$refs.instance_template_canvas.canvas_ctx.canvas

      },
      reset_drawing: function(){
        // TODO: this can become an interaction in the future.
        if(this.instance.type === 'keypoints'){
          this.instance.is_drawing_edge = false;
          this.instance.is_moving = false;
          this.instance.is_node_hovered = false;
          this.instance.is_dragging_instance = false;
        }
      },
      key_down_handler: function (e) {

        if (e.keyCode === 27) {
          e.preventDefault();
          if(this.$refs['instance_template_creation_toolbar']){
            this.$refs['instance_template_creation_toolbar'].draw_mode = !this.$refs['instance_template_creation_toolbar'].draw_mode;
            this.$refs['instance_template_creation_toolbar'].edit_mode_toggle();
            this.reset_drawing()
          }

        }
      },
      update_draw_mode_on_instances: function (draw_mode) {
        this.instance_context.draw_mode = draw_mode;
      },
      close: function () {
        window.removeEventListener('keydown', this.key_down_handler)
        this.is_open = false;
      },
      instance_hover_update(index, type){
        if (this.lock_point_hover_change == true) {return}
        // important, we don't change the value if it's locked
        // otherwise it's easy for user to get "off" of the point they want

        if (index != null) {
          this.instance_hover_index = parseInt(index)
          this.instance_hover_type = type   // ie polygon, box, etc.
        }
        else{
          this.instance_hover_index = null;
          this.instance_hover_type = null;
        }
      },
      generate_interaction_from_event(event){
        const interaction_generator = new InstanceTemplateCreationInteractionGenerator(
          event,
          this.instance_hover_index,
          this.instance_list,
          this.$refs['instance_template_creation_toolbar'].draw_mode,
          this.instance,
        )
        return interaction_generator.generate_interaction();
      },
      mouse_move: function (event) {
        const interaction = this.generate_interaction_from_event(event);
        if(interaction){
          interaction.process();
        }
      },
      mouse_down: function (event) {

        const interaction = this.generate_interaction_from_event(event);
        if(interaction){
          interaction.process();
        }

      },
      double_click: function (event) {
        this.instance.double_click(event);
      },
      mouse_up: function (event) {
        const interaction = this.generate_interaction_from_event(event);
        if(interaction){
          interaction.process();
        }
      },
      contextmenu: function (event) {
        this.instance.contextmenu(event);
      },
      validate_empty_instance_list() {
        // Checks if all the instances in the instance list are non-empty.
        let result = true;
        this.instance_list.forEach(inst => {
          // TODO VALIDATE OTHER INSTANCE TYPES
          if (inst.type === 'keypoints') {
            if (inst.nodes.length === 0 && inst.edges.length === 0) {
              this.error = {keypoints: 'Please add at least one point.'}
              result = false;
            }
          }
        })
        return result
      },
      save_instance_template: function(){
        if(this.$props.instance_template){
          this.update_instance_template()
        }
        else{
          this.create_instance_template()
        }
      },
      update_instance_template: async function () {
        try {
          this.error = {};
          const has_empty_instances = this.validate_empty_instance_list();
          if(!has_empty_instances){
            return
          }
          if(!this.name){
            this.error = {'name': 'Please provide a name for the instance template.'}
            return
          }
          if(!this.$props.instance_template){
            return
          }

          const response = await axios.post(
            `/api/v1/project/${this.$props.project_string_id}/instance-template/${this.$props.instance_template.id}`,
            {
              name: this.name,
              instance_list: this.instance_list.map(inst => inst.get_instance_data()),

            })
          if (response.status === 200) {
            this.is_open = false;
            this.$emit('instance_template_create_success', response.data.instance_template);
          }
        } catch (error) {
          console.error(error)
          this.error = this.$route_api_errors(error)

        } finally {
          this.loading = false
        }
      },
      create_instance_template: async function () {
        try {
          this.error = {};
          const has_empty_instances = this.validate_empty_instance_list();
          if(!has_empty_instances){
            return
          }
          if(!this.name){
            this.error = {'name': 'Please provide a name for the instance template.'}
            return
          }

          const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/instance-template/new`,
            {
              name: this.name,
              reference_height: this.canvas_height,
              reference_width: this.canvas_width,
              instance_list: this.instance_list.map(inst => inst.get_instance_data()),

            })
          if (response.status === 200) {
            this.name = [];
            this.is_open = false;
            this.$emit('instance_template_create_success', response.data.instance_template);
          }
        } catch (error) {
          console.error(error)
          this.error = this.$route_api_errors(error)

        } finally {
          this.loading = false
        }
      }
    },

    computed: {
      instance_list() {
        if (this.instance) {
          return [this.instance]
        }
        return []
      }
    }

  })
</script>

<style>
  .dialog-instance-template{
    max-height: 100% !important;
    overflow: inherit !important;
  }
</style>
