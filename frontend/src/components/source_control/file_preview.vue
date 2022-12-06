<template>

  <div class="ma-1 pa-0">

    <div
      v-if="file.type === 'image'"
      class="pa-0 ma-0 drawable-wrapper"
      :style="{border: selected ? '4px solid #1565c0' : '4px solid #e0e0e0', height: `${file_preview_height + 8}px`, position: 'relative'}"
      ref="file_card"

    >
      <file_preview_details_card
        v-if="show_preview_details"
        :file="file"
        :file_preview_height="file_preview_height"
        :file_preview_width="file_preview_width"
      ></file_preview_details_card>
      <drawable_canvas
        v-if="file.type === 'image'"
        ref="drawable_canvas"
        :allow_zoom="false"
        :image_bg="image_bg"
        :rotation_degrees="file.image.rotation_degrees"
        :canvas_height="file_preview_height"
        :canvas_width="file_preview_width"
        :editable="false"
        :auto_scale_bg="true"
        :refresh="refresh"
        :canvas_wrapper_id="`canvas_wrapper__${file.id}__${file_preview_width}__${file_preview_height}`"
        :canvas_id="`canvas__${file.id}__${file_preview_width}__${file_preview_height}`"
        @canvas_element_ready="on_canvas_elm_ready"
      >

        <instance_list
          slot-scope="props"
          :instance_list="filtered_instance_list"
          :vertex_size="3"
          :refresh="refresh"
          :video_mode="false"
          :label_settings="label_settings"
          :show_annotations="true"
          :draw_mode="false"
          :canvas_transform="props.canvas_transform"
          slot="instance_drawer"
        />

      </drawable_canvas>
      <v-skeleton-loader
        v-else
        type="image"
        :width="file_preview_width"
        :height="file_preview_height"
      />
    </div>
    <div
      v-if="file.type === 'video'"
      class="pa-0 ma-0 drawable-wrapper"
      :style="{border: selected ? '4px solid #1565c0' : '4px solid #e0e0e0', height: `${file_preview_height + 8}px`, position: 'relative'}"
      ref="file_card">
      <file_preview_details_card
        v-if="show_preview_details"
        :file="file"
        :file_preview_height="file_preview_height"
        :file_preview_width="file_preview_width"
      ></file_preview_details_card>
      <video_drawable_canvas
        :allow_zoom="false"
        :preview_mode="true"
        :project_string_id="project_string_id"
        :filtered_instance_by_model_runs="filtered_instance_list"
        :video="file.video"
        :file="file"
        :canvas_height="file_preview_height"
        :canvas_width="file_preview_width"
        :editable="false"
        :auto_scale_bg="true"
        :video_player_height="80"
        :label_settings="label_settings"
        :refresh="refresh"
        :show_video_nav_bar="show_video_nav_bar"
        :canvas_wrapper_id="`canvas_wrapper__${file.id}__${file_preview_width}__${file_preview_height}`"
        :canvas_id="`canvas__${file.id}__${file_preview_width}__${file_preview_height}`"
        @on_click_details="view_file_details"
        ref="video_drawable_canvas"
        @update_instance_list="set_video_instance_list"
      >
      </video_drawable_canvas>
    </div>
    <div
      v-if="file.type === 'text'"
      class="pa-0 ma-0 drawable-wrapper"
      :style="{border: selected ? '4px solid #1565c0' : '4px solid #e0e0e0', height: `${file_preview_height + 8}px`, position: 'relative'}"
      ref="file_card"

    >
      <file_preview_details_card
        v-if="show_preview_details"
        :file="file"
        :file_preview_height="file_preview_height"
        :file_preview_width="file_preview_width"
      ></file_preview_details_card>
      <div v-if="file.type === 'text'" :style="`width: ${file_preview_width}; position: relative;`">
        <v-icon :size="file_preview_width" class="ma-0 pa-0">
          mdi-script-text
        </v-icon>

      </div>
      <v-skeleton-loader
        v-else
        type="image"
        :width="128"
        :height="128"
      />
    </div>
    <div v-if="file.type === 'compound'"
         class="pa-0 ma-0 drawable-wrapper"
         :style="{border: selected ? '4px solid #1565c0' : '4px solid #e0e0e0', height: `${file_preview_height + 8}px`}"
         ref="file_card">
      <compound_file_preview
        :show_preview_details="show_preview_details"
        :project_string_id="project_string_id"
        :file="file"
        :base_model_run="base_model_run"
        :compare_to_model_run_list="compare_to_instance_list_set"
        :enable_go_to_file_on_click="enable_go_to_file_on_click"
        :file_preview_height="file_preview_height"
        :file_preview_width="file_preview_width"
        :show_ground_truth="show_ground_truth"
        :show_video_nav_bar="show_video_nav_bar"
      />
    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

import instance_list from "../vue_canvas/instance_list";
import drawable_canvas from "../vue_canvas/drawable_canvas";
import video_drawable_canvas from "../vue_canvas/video_drawable_canvas";
import {InstanceContext} from "../../../embed/src/types/instances/InstanceContext";
import Compound_file_preview from "@/components/source_control/compound_file_preview";
import file_preview_details_card from "@/components/source_control/file_preview_details_card";
import {
  filter_global_instance_list
} from "./dataset_explorer_instance_filtering";
import {initialize_instance_object} from "../../../embed/src/types/utils/instance_utils";
import {SUPPORTED_CLASS_INSTANCE_TYPES} from "@/components/vue_canvas/instances/Instance";
import {InstanceImage2D} from "@/components/vue_canvas/instances/InstanceImage2D";
import {newEmptyCanvasMouseCtx} from "../../../embed/src/types/annotation/image/MousePosition";
import {post_init_instance} from "../../../embed/src/types/utils/instance_utils";

export default Vue.extend({
  name: "file_preview",
  components: {
    Compound_file_preview,
    file_preview_details_card,
    video_drawable_canvas,
    drawable_canvas,
    instance_list
  },
  props: {
    'project_string_id': {
      default: undefined
    },
    'file': {
      default: undefined
    },
    'instance_list': {
      default: undefined
    },
    'file_preview_width': {
      default: 440
    },
    'show_preview_details': {
      default: true
    },
    'selectable': {
      default: false
    },
    'selected': {
      default: false
    },
    'file_preview_height': {
      default: 325
    },
    'base_model_run': {
      default: null
    },
    'compare_to_model_run_list': {
      default: null
    },
    'show_ground_truth': {
      default: true
    },
    show_video_nav_bar: {
      default: true
    },
    'video': {
      default: null
    },
    'enable_go_to_file_on_click': {
      default: true
    }
  },
  data: function () {
    return {
      image_bg: undefined,
      global_instance_rerender: 0,
      refresh: null,
      filtered_instance_list: [],
      label_file_colour_map: {},
      label_file_map: {},
      video_instance_list: [],
      canvas_mouse_ctx: null,
      canvas_elm: null,
      instance_context: new InstanceContext(),
      compare_to_instance_list_set: [],
      label_settings: {
        font_size: 20,
        show_removed_instances: false,
        spatial_line_size: 2,
        show_text: false,
        show_label_text: false,
        show_attribute_text: false,
      }
    }
  },
  created() {
    this.canvas_mouse_ctx = newEmptyCanvasMouseCtx()

  },

  async mounted() {
    if (this.$props.file) {
      try {
        await this.set_bg(this.$props.file);
      } catch (e) {
        console.error(e)
      }

    }
    if (this.$refs.file_card) {
      if (this.$props.selectable) {
        this.$refs.file_card.addEventListener('dblclick', this.view_file_details)
        this.$refs.file_card.addEventListener('click', this.select_file)
      } else {
        this.$refs.file_card.addEventListener('click', this.view_file_details)
      }
    }

    await this.$nextTick()

  },
  watch: {
    file: {
      deep: true,
      immediate: false,
      handler: async function (new_val, old_val) {
        await this.set_bg(new_val);
        this.build_label_file_map()
        this.prepare_filtered_instance_list();
      }
    },
    base_model_run: function () {
      this.prepare_filtered_instance_list();
    },
    compare_to_model_run_list: function () {
      this.prepare_filtered_instance_list();
    },
    show_ground_truth: function () {
      this.prepare_filtered_instance_list();
    }
  },
  methods: {
    select_file: function () {

      this.$emit('file_selected', this.$props.file)
    },
    set_video_instance_list: function (new_list) {
      this.video_instance_list = new_list;
      this.prepare_filtered_instance_list();
      this.refresh = Date.now()
    },
    instance_hovered: function () {

    },
    instance_unhovered: function () {

    },
    initialize_instance: function (instance) {

      let inst = initialize_instance_object(instance, this.canvas_mouse_ctx)

      inst = post_init_instance(inst,
        this.label_file_map,
        this.canvas_element,
        this.canvas_mouse_ctx.label_settings,
        this.canvas_mouse_ctx.canvas_transform,
        this.instance_hovered,
        this.instance_unhovered,
        this.$refs.drawable_canvas.canvas_mouse_tools)
      return inst
    },
    build_label_file_map: function () {
      if(!this.file || !this.file.instance_list){
        return
      }
      this.label_file_colour_map = {}
      for (let inst of this.file.instance_list) {
        if (inst.label_file) {
          this.label_file_colour_map[inst.label_file_id] = inst.label_file.colour
          this.label_file_map[inst.label_file_id] = inst.label_file
        }
      }
    },
    prepare_filtered_instance_list: function () {
      this.build_label_file_map()
      this.filtered_instance_list = []
      this.filtered_instance_list = filter_global_instance_list(
        this.filtered_instance_list,
        this.get_global_instance_list(),
        this.$props.base_model_run,
        this.$props.compare_to_model_run_list,
        this.$props.show_ground_truth
      )


    },

    set_bg: async function (newFile) {
      return new Promise((resolve, reject) => {
        if (!newFile) {
          this.image_bg = undefined;
          this.refresh = new Date();
          resolve();
        } else {
          if (newFile.image && newFile.image.url_signed) {
            const image = new Image();
            image.onload = () => {
              this.image_bg = image;
              this.refresh = new Date();
              image.onload = () => resolve(image)
            }
            image.src = this.$props.file.image.url_signed;
            image.onerror = reject
          } else {
            resolve();
          }

        }
      })

    },
    get_global_instance_list: function () {
      // This instance list can either be the image instance list of the video instance list at current frame.

      if(!this.canvas_elm){
        return []
      }
      let result = []
      if (this.$props.instance_list) {
        if (this.$props.file.image) {
          result = this.$props.instance_list;
        }
      }
      if (this.$props.file.video) {
        result = this.video_instance_list;
      }
      return result.map(inst => {

        let newInst = initialize_instance_object(inst, this.canvas_mouse_ctx)
        newInst = post_init_instance(newInst,
          this.label_file_map,
          this.canvas_elm,
          this.canvas_mouse_ctx.label_settings,
          this.canvas_mouse_ctx.canvas_transform,
          this.instance_hovered,
          this.instance_unhovered)
        return newInst
      })
    },
    on_canvas_elm_ready: function(canvas_elm){
      this.canvas_elm = canvas_elm
      this.prepare_filtered_instance_list()
      this.$forceUpdate()
      this.$refs.drawable_canvas.update_canvas()
      this.refresh = new Date()

    },
    view_file_details: function (current_frame) {
      if (this.$props.enable_go_to_file_on_click == false) {
        return
      }
      let model_runs = [];
      let color_list = [];
      if (this.base_model_run) {
        model_runs.push(this.$props.base_model_run)
        color_list.push(this.$props.base_model_run.color)
      }
      if (this.$props.compare_to_model_run_list) {
        model_runs = model_runs.concat(this.$props.compare_to_model_run_list);
        color_list = color_list.concat(this.$props.compare_to_model_run_list.map(m => m.color));
      }
      const model_run_ids = model_runs.map(run => run.id);
      this.$router.push({
        path: `/studio/annotate/${this.$props.project_string_id}`,
        query: {
          file: this.$props.file.id,
          model_runs: model_runs.length > 0 ? encodeURIComponent(model_run_ids) : undefined,
          color_list: color_list.length > 0 ? encodeURIComponent(color_list) : undefined,
          frame: this.$props.file.type === 'video' ? 0 : undefined

        }
      }).catch(() => {
      });
      this.$emit('view_file_detail', this.$props.file, model_runs, color_list)
    }


  },
  computed: {

  },
});
</script>

<style>
.drawable-wrapper:hover {
  cursor: pointer;
}
</style>
