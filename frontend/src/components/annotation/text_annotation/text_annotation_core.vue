<template>
<div
  :ref="`text_annotation_area_${working_file.id}`"
  style="display: flex; flex-direction: row"
>
  <conversational_meta
    v-if="!image_annotation_ctx.rendering && !image_annotation_ctx.resizing && annotation_ui_context.subtype === 'conversational'"
    :workign_file="working_file"
    :global_attribute_groups_list="global_attribute_groups_list"
    :annotation_ui_context="annotation_ui_context"
  />
  <div style="display: flex; flex-direction: column">
    <div style="display: flex; flex-direction: row">
      <text_fast_label
        v-if="show_label_selection"
        :rects="selection_rects"
        :arrow_position="render_drawing_arrow && render_drawing_arrow.arrow ? render_drawing_arrow.arrow : null"
        :label_list="label_list"
        :svg_ref="$refs[`initial_svg_element_${this.working_file.id}`]"
        @create_instance="on_popup_create_instance"
        @create_relation="create_relation"
      />
      <text_context_menu
        v-if="context_menu"
        :context_menu="context_menu"
        @delete_instance="delete_instance"
      />
      <div style="width: 100%; display: flex; flex-direction: column">
        <v-progress-linear
          v-if="!fetching_error && (image_annotation_ctx.resizing || image_annotation_ctx.rendering)"
          indeterminate
        />
        <v_error_multiple
          v-if="fetching_error"
          :error="['Error occured while dowloading text file']"
        />
        <svg
          :ref="`initial_svg_element_${working_file.id}`"
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
          direction="ltr"
          id="svg0:60"
          :style="`height: ${lines && lines.length > 0 ? lines[lines.length - 1].y + 60 : 10}px; width: ${real_container_width}px`"
          :class="unselectable && 'unselectable'"
          @mouseup="trigger_mouseup"
          @mousedown="trigger_mousedown"
        >
          <g v-if="image_annotation_ctx.rendering && initial_words_measures" :transform="`translate(0, ${render_offset})`">
            <text
              v-for="(word, index) in initial_words_measures"
              :key="word.value + index"
              :ref="`word_${index}_file_${working_file.id}`"
              x="40"
              y="5"
              fill="white"
              text-anchor="middle">
              {{ word.value }}
            </text>
          </g>
          <g v-if="image_annotation_ctx.resizing && initial_words_measures" :transform="`translate(0, ${render_offset})`">
            <text
              v-for="(word, index) in initial_words_measures"
              :key="word.value + index"
              :ref="`word_${index}_file_${working_file.id}`"
              x="40"
              y="5"
              fill="white"
              text-anchor="middle">
              {{ word.value }}
            </text>
          </g>
          <g ref="main-text-container" :transform="`translate(0, ${render_offset})`" v-else>
            <relation_in_progress
              v-if="relation_drawing"
              :render_drawing_arrow="render_drawing_arrow"
            />
            <g v-if="render_rects && render_rects.length > 0">
              <g
                v-for="instance in instance_list.get().filter(instance => !instance.soft_delete && !invisible_labels.includes(instance.label_file_id))"
                :key="`instance_rect_${instance.get_instance_data().id}`"
              >
                <rect
                  v-if="get_instance_rects(instance)"
                  :x="get_instance_rects(instance).x"
                  :y="get_instance_rects(instance).y - 15"
                  :fill="annotation_ui_context.get_current_ann_ctx().hover_instance && (annotation_ui_context.get_current_ann_ctx().hover_instance.get_instance_data().id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.from_instance_id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.to_instance_id === instance.get_instance_data().id) ? 'rgba(255, 0, 0, 0.2)' : `rgba(${instance.label_file.colour.rgba.r}, ${instance.label_file.colour.rgba.g}, ${instance.label_file.colour.rgba.b}, 0.2)`"
                  :width="instance.label_file.label.name.length * 8"
                  :height="15"
                  @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
                  @mousedown="(e) => on_trigger_instance_click(e, instance.get_instance_data().id)"
                  @mouseleave="on_instance_stop_hover"
                  @contextmenu="(e) => on_open_context_menu(e, instance)"
                  style="font-size: 10px; cursor: pointer"
                  class="unselectable"
                />
              </g>
              <g
                v-for="(instance, instance_index) in instance_list.get().filter(instance => !instance.soft_delete && !invisible_labels.includes(instance.label_file_id))"
                :key="`instance_${instance.get_instance_data().id}`"
              >
                <text
                  v-if="get_instance_rects(instance)"
                  :data-cy="`text_label_${instance_index}`"
                  :x="get_instance_rects(instance).x + 2"
                  :y="get_instance_rects(instance).y - 3"
                  :fill="annotation_ui_context.get_current_ann_ctx().hover_instance && (annotation_ui_context.get_current_ann_ctx().hover_instance.get_instance_data().id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.from_instance_id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                  @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
                  @mousedown="(e) => on_trigger_instance_click(e, instance.get_instance_data().id)"
                  @mouseleave="on_instance_stop_hover"
                  @contextmenu="(e) => on_open_context_menu(e, instance)"
                  style="font-size: 10px; cursor: pointer;"
                  class="unselectable"
                >
                  {{ instance.label_file.label.name }}
                </text>
              </g>
              <g
                v-for="instance in instance_list.get().filter(instance => !instance.soft_delete && instance.type === 'relation' && !invisible_labels.includes(instance.label_file_id))"
                :key="`rel_start_${instance.get_instance_data().id}`"
              >
                <g
                  v-if="get_instance_rects(instance)"
                >
                  <rect
                    :x="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x"
                    :y="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y"
                    :fill="annotation_ui_context.get_current_ann_ctx().hover_instance && (annotation_ui_context.get_current_ann_ctx().hover_instance.get_instance_data().id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.from_instance_id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                    :width="1"
                    :height="10"
                    @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
                    @mousedown="(e) => on_trigger_instance_click(e, instance.get_instance_data().id)"
                    @mouseleave="on_instance_stop_hover"
                    @contextmenu="(e) => on_open_context_menu(e, instance)"
                    style="font-size: 10px; cursor: pointer"
                    class="unselectable"
                  />
                  <circle
                    :cx="insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).x + render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).width"
                    :cy="insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y + 10 : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).y + 10"
                    :fill="annotation_ui_context.get_current_ann_ctx().hover_instance && (annotation_ui_context.get_current_ann_ctx().hover_instance.get_instance_data().id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.from_instance_id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                    r="2"
                    class="unselectable"
                  />
                  <rect
                    :x="render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).x + render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).width"
                    :y="render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).y"
                    :fill="annotation_ui_context.get_current_ann_ctx().hover_instance && (annotation_ui_context.get_current_ann_ctx().hover_instance.get_instance_data().id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.from_instance_id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                    :width="1"
                    :height="10"
                    @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
                    @mousedown="(e) => on_trigger_instance_click(e, instance.get_instance_data().id)"
                    @mouseleave="on_instance_stop_hover"
                    style="font-size: 10px; cursor: pointer"
                    class="unselectable"
                  />
                  <path
                    :d="`M ${!insatance_orientation_direct(instance) ? get_instance_rects(instance).x : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).x + render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).width} ${!insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y + 10 : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).y + 10} l -5, -5 l 10, 0 l -5, 5`"
                    :fill="annotation_ui_context.get_current_ann_ctx().hover_instance && (annotation_ui_context.get_current_ann_ctx().hover_instance.get_instance_data().id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.from_instance_id === instance.get_instance_data().id || annotation_ui_context.get_current_ann_ctx().hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                    class="unselectable"
                  />
                </g>
              </g>
              <rect
                v-for="rect in render_rects"
                :key="`rect_x_${rect.x}_y_${rect.y}_width_${rect.width}`"
                :fill="annotation_ui_context.get_current_ann_ctx().hover_instance && (annotation_ui_context.get_current_ann_ctx().hover_instance.get_instance_data().id === rect.instance_id || annotation_ui_context.get_current_ann_ctx().hover_instance.from_instance_id === rect.instance_id || annotation_ui_context.get_current_ann_ctx().hover_instance.to_instance_id === rect.instance_id) ? 'red' : rect.color"
                :x="rect.x"
                :y="rect.y"
                :width="rect.width"
                @mouseenter="() => on_instance_hover(rect.instance_id)"
                @mousedown="() => on_trigger_instance_click(rect.instance_id)"
                @mouseleave="on_instance_stop_hover"
                @contextmenu="(e) => on_open_context_menu(e, instance)"
                :height="rect.instance_type === 'text_token' ? 3 : 1"
                style="cursor: pointer"
                class="unselectable"
              />
            </g>
            <g
              v-for="(line, index) in lines"
              :transform="`translate(0, ${25 + line.y})`"
              :key="`line_${index}`"
            >
              <text
                v-for="(token, token_index) in tokens.filter(token => token.line === index)"
                :id="token.id"
                :key="`line_${index}token_${token_index}`"
                :data-cy="`token_${token_index}_line_${index}`"
                :x="token.start_x"
                :fill="annotation_ui_context.get_current_ann_ctx().hover_instance &&
                              (
                                  (annotation_ui_context.get_current_ann_ctx().hover_instance.start_token <= token.id && token.id <= annotation_ui_context.get_current_ann_ctx().hover_instance.end_token) ||
                                  (annotation_ui_context.get_current_ann_ctx().hover_instance.start_token >= token.id && token.id >= annotation_ui_context.get_current_ann_ctx().hover_instance.end_token)
                              ) ? 'red' : 'black'"
              >
                {{ token.word }}
              </text>
            </g>
            <text_selection_svg
              v-if="selection_rects"
              :rects="selection_rects"
              :svg_ref="$refs[`initial_svg_element_${this.working_file.id}`]"
              @on_change_selection_border="on_change_selection_border"
              @on_start_moving_borders="on_start_moving_borders"
              @on_selection_click="on_selection_click"
            />
          </g>
        </svg>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import Vue from "vue";
import text_toolbar from "./text_toolbar.vue"
import text_sidebar from "./text_sidebar.vue"
import text_selection_svg from "./render_elements/selection.vue"
import text_fast_label from "./render_elements/fast_label_menu.vue"
import text_context_menu from "./render_elements/text_context_menu.vue"
import relation_in_progress from "./render_elements/relation_in_progress.vue"
import conversational_meta from "./render_elements/conversational_meta.vue"
import {TextAnnotationInstance, TextRelationInstance} from "../../vue_canvas/instances/TextInstance"
import {getInstanceList} from "../../../services/instanceList"
import getTextService from "../../../services/getTextService"
// New command pattern
import InstanceList from "../../../helpers/instance_list"
import {
  CreateInstanceCommand,
  DeleteInstanceCommand,
  UpdateInstanceLabelCommand,
  UpdateInstanceAttributeCommand,
  UpdateGlobalAttributeCommand
} from "../../../helpers/command/available_commands"
import DrawRects from "./text_utils/draw_rects";
import closest_token from "./text_utils/closest_token"
import { Instance } from "../../vue_canvas/instances/Instance";
import { v4 as uuidv4 } from 'uuid'

export default Vue.extend({
  name: "text_annotation_core",
  components: {
    text_toolbar,
    text_sidebar,
    text_selection_svg,
    text_fast_label,
    text_context_menu,
    relation_in_progress,
    conversational_meta
  },
  props: {
    image_annotation_ctx: {
      type: Object,
      required: true
    },
    instance_store: {
      type: Object,
      required: true
    },
    working_file: {
      type: Object,
      default: undefined
    },
    task: {
      type: Object,
      default: undefined
    },
    job_id: {
      type: Number,
      default: undefined
    },
    label_file_colour_map: {
      type: Object,
      required: true
    },
    label_list: {
      type: Array,
      required: true
    },
    project_string_id: {
      type: String,
      required: true
    },
    global_attribute_groups_list: {
      type: Array,
      required: true
    },
    per_instance_attribute_groups_list: {
      type: Array,
      required: true
    },
    label_schema: {
      type: Object,
      default: {}
    },
    annotation_ui_context: {
      type: Object,
      default: null
    },
    history: {
      type: Object,
      default: null
    },
    has_changed: {
      type: Boolean,
      default: false
    },
    save_loading: {
      type: Boolean,
      default: false
    },
    bulk_mode: {
      type: Boolean,
      default: false
    },
    search_mode: {
      type: Boolean,
      default: false
    },
    container_width: {
      type: Number,
      default: 600
    },
    container_height: {
      type: Number,
      default: 600
    },
    child_annotation_ctx_list: {
      type: Array,
      default: []
    }
  },
  data() {
    return {
      fetching_error: false,
      text: null,
      current_label: null,
      relation_drawing: false,
      initial_words_measures: null,
      lines: [],
      tokens: [],
      invisible_labels: [],
      //Helpers
      instance_in_progress: null,
      path: {},
      //Render constants
      additional_line_space: 30,
      show_default_navigation: true,
      unselectable: false,
      text_field_width: '100%',
      re_render_func: undefined,
      selection_rects: null,
      selection_rects_next_token: null,
      show_label_selection: false,
      moving_border: false,
      context_menu: null,
      render_offset: 23.5,

      current_global_instance: null,

      // New command pattern
      instance_list: undefined,
    }
  },
  beforeMount() {
    // this.resize_listener()
  },
  mounted() {
    this.on_mount()
    this.start_autosave()
    this.$emit('trigger_listeners_setup')
  },
  computed: {
    real_container_width: function() {
      if (this.container_width) return this.container_width - 30
      else return window.innerWidth - 350
    },
    render_rects: function () {
      if (this.image_annotation_ctx.rendering || this.image_annotation_ctx.resizing) return [];
      if (this.tokens.length === 0) return [];
      if (!this.instance_list) return [];

      let rects_to_draw = [];
      this.instance_list.get().filter(instance => !instance.soft_delete && !this.invisible_labels.includes(instance.label_file_id)).map(instance => {
        const instance_rects = this.draw_instance(instance)
        rects_to_draw = [...rects_to_draw, ...instance_rects]
      })

      this.find_intersections(rects_to_draw)
      rects_to_draw = [];
      this.instance_list.get().filter(instance => !instance.soft_delete && !this.invisible_labels.includes(instance.label_file_id)).map(instance => {
        const instance_rects = this.draw_instance(instance)
        rects_to_draw = [...rects_to_draw, ...instance_rects]
      })
      this.find_intersections(rects_to_draw)

      if (this.selection_rects_next_token) this.on_select_text(this.selection_rects_next_token, this.selection_rects_next_token)
      return rects_to_draw
    },
    render_drawing_arrow: function () {
      if (!this.instance_in_progress) return {}

      const inst = this.render_rects.find(rect => rect.instance_id === this.instance_in_progress.start_instance)

      if (!inst) return {}

      const bounding_rect = this.$refs[`initial_svg_element_${this.working_file.id}`].getBoundingClientRect()

      const { x, y } = inst

      if (this.path.x && this.path.y) {
        return {
          marker: {
            x,
            y
          },
          arrow: {
            x: this.path.x - bounding_rect.x,
            y: this.path.y - bounding_rect.y - this.render_offset + 5
          },
          path: `M ${x} ${y} Q ${this.path.x - bounding_rect.x - 100} ${this.path.y - bounding_rect.y - 30} ${this.path.x - bounding_rect.x} ${this.path.y - bounding_rect.y - this.render_offset}`
        }
      }

      return {
        marker: {
          x,
          y
        }
      }
    },
    undo_disabled: function () {
      return !this.history || !this.history.undo_posible
    },
    redo_disabled: function () {
      return !this.history || !this.history.redo_posible
    }
  },
  watch: {
    initial_words_measures: function(newVal) {
      if (newVal) {
        this.image_annotation_ctx.rendering = true
        setTimeout(this.initialize_token_render, 1000)
      }
    },
    instance_list: function (newVal) {
      if (this.working_file.type === "text" && newVal) {
        this.instance_store.set_instance_list(this.working_file.id, newVal)
        this.instance_store.set_file_type(this.working_file.id, this.working_file.type)
        this.$emit('instance_list_updated', newVal, this.working_file.id, this.working_file.type)
      }
    },
    working_file: function () {
      this.image_annotation_ctx.rendering = true
      this.text = null;
      this.initial_words_measures = null;
      this.lines = []
      this.show_label_selection = false
      this.selection_rects = null
      this.on_mount()
    },
    task: function () {
      this.image_annotation_ctx.rendering = true
      this.text = null;
      this.initial_words_measures = null;
      this.lines = []
      this.show_label_selection = false
      this.selection_rects = null
      this.on_mount()
    }
  },
  methods: {
    on_selection_click: function(e) {
      const draw_class = new DrawRects(this.tokens, this.lines, this.instance_list)
      const coordinates = {
        x: e.clientX - 350,
        y: e.clientY - 100 - 40
      }
      const clicked_token = closest_token(this.tokens, this.lines, coordinates)
      this.selection_rects = draw_class.generate_selection_rect(clicked_token.id, clicked_token.id)
    },
    get_instance_rects: function(instance) {
      const rects = this.render_rects.find(rect => rect.instance_id === instance.get_instance_data().id)
      return rects
    },
    on_start_moving_borders: function() {
      this.show_label_selection = false
      this.moving_border = true
    },
    on_change_selection_border: function(start_coordinates, end_coordinates) {
      const draw_class = new DrawRects(this.tokens, this.lines, this.instance_list)
      let start_token_id;
      let end_token_id;

      if (start_coordinates) {
        start_token_id = closest_token(this.tokens, this.lines, start_coordinates).id
        end_token_id = this.selection_rects[0].end_token_id
      }

      if (end_coordinates) {
        start_token_id = this.selection_rects[0].start_token_id
        end_token_id = closest_token(this.tokens, this.lines, end_coordinates).id
      }

      this.instance_in_progress.start_token = start_token_id
      this.instance_in_progress.end_token = end_token_id

      this.selection_rects = draw_class.generate_selection_rect(start_token_id, end_token_id)

      this.show_label_selection = true
      this.moving_border = false
    },
    on_open_context_menu: function(e, instance) {
      e.preventDefault()
      const bounding_rect = this.$refs[`initial_svg_element_${this.working_file.id}`].getBoundingClientRect()
      this.context_menu = {
        x: e.clientX - bounding_rect.left + 200 < bounding_rect.width ? e.clientX - bounding_rect.x : e.clientX - bounding_rect.x - 200,
        y: e.clientY - bounding_rect.top + 25,
        instance
      }
      this.selection_rects = null
      this.show_label_selection = false
      this.annotation_ui_context.get_current_ann_ctx().current_instance = instance
    },
    on_change_label_schema: function(schema){
      this.$emit('change_label_schema', schema)
    },
    bulk_labeling: function (instance_id) {
      const instance = this.instance_list.get().find(inst => {
        const {id} = inst.get_instance_data()
        if (id === instance_id) return inst
      })
      if (instance.start_token !== instance.end_token) return;

      const instance_word = this.tokens.find(token => token.id === instance.start_token).word
      let same_token_indexes = [];
      this.tokens.map((token, index) => {
        if (token.word.toLowerCase() === instance_word.toLowerCase() && token.id !== instance.start_token) same_token_indexes.push(index)
      })

      const newly_created_instances = [];
      const working_insatnce_list = this.instance_list.get().filter(inst => inst.type === "text_token")
      same_token_indexes.map(index => {
        const instance_already_exists = working_insatnce_list.find(inst => inst.start_token === this.tokens[index].id && inst.end_token === this.tokens[index].id)
        if (!instance_already_exists) {
          const created_instance = new TextAnnotationInstance();
          created_instance.create_frontend_instance(
            this.tokens[index].id,
            this.tokens[index].id,
            {...instance.label_file}
          )

          newly_created_instances.push(created_instance)
        }
      })

      if (newly_created_instances.length > 0) {
        this.instance_list.push(newly_created_instances)
        const new_command = new CreateInstanceCommand(newly_created_instances, this.instance_list)
        this.annotation_ui_context.command_manager.executeCommand(new_command)

        this.$emit('set_has_changed', true)
      }
    },
    resize_listener: function () {
      this.child_annotation_ctx_list.map(child_context => {
        child_context.resizing = true
      })
      this.lines = []
      this.tokens = []
      this.selection_rects = null
      this.show_label_selection = false
      this.instance_in_progress = null
      clearTimeout(this.re_render_func);
      this.re_render_func = setTimeout(this.initialize_token_render, 1000)
    },
    leave_listener: function (e) {
      if (this.has_changed || this.save_loading) {
        const confirmationMessage = "\o/";

        (e || window.event).returnValue = confirmationMessage;
        return confirmationMessage;
      }
    },
    keydown_event_listeners: async function (e) {
      const current_context = this.annotation_ui_context.get_current_ann_ctx()
      if (e.keyCode === 83) {
        this.$emit('save')
      } else if (e.keyCode === 71) {
        current_context.search_mode = true;
      } else if (e.keyCode === 66) {
        current_context.bulk_mode = true
      }
    },
    keyup_event_listeners: function (e) {
      const current_context = this.annotation_ui_context.get_current_ann_ctx()

      if (e.keyCode === 71) {
        current_context.search_mode = false;
      } else if (e.keyCode === 66) {
        current_context.bulk_mode = false
      }

      this.key_up_unremovable_listeners(e)
    },
    key_up_unremovable_listeners: function(e) {
      if (e.keyCode === 27) {
        this.annotation_ui_context.get_current_ann_ctx().current_instance = null
        this.instance_in_progress = null
        this.path = {};
        this.unselectable = false
        this.relation_drawing = false;
        this.selection_rects = null;
        this.show_label_selection = false;
        this.context_menu = null
        window.removeEventListener('mousemove', this.draw_relation_listener)
      }
      else if (e.keyCode === 37 && this.selection_rects) {
        this.on_select_text(this.selection_rects[0].start_token_id - 1, this.selection_rects[0].start_token_id - 1, "left")
      } else if (e.keyCode === 39 && this.selection_rects) {
        const token_id = this.get_next_toke_id(this.selection_rects[0].end_token_id)
        this.on_select_text(token_id, token_id)
      }
    },
    get_next_toke_id: function(id) {
      let working_id = id
      let token_id;

      const last_token_id = this.tokens[this.tokens.length -1].id
      if (last_token_id <= working_id) return last_token_id

      while (!token_id) {
        const token = this.tokens.find(token => token.id === working_id + 1)
        if (token) {
          token_id = token.id
        }
        working_id += 1
      }

      return token_id
    },
    start_autosave: function () {
      this.interval_autosave = setInterval(
        this.detect_is_ok_to_save,
        15 * 1000
      );
    },
    detect_is_ok_to_save: async function () {
      if (this.has_changed && !this.instance_in_progress) {
        this.$emit('save')
      }
    },
    trigger_mousedown: function(e) {
      const click_on_selection = ['circle', 'rect'].includes(e.target.localName)
      if (!click_on_selection && this.selection_rects) {
        this.selection_rects = null
        this.show_label_selection = null
      }
    },
    trigger_mouseup: function (e) {
      if (this.search_mode) return this.search_in_google(e)
      if (this.selection_rects && !e.target.nodeName.includes('text')) return;
      if (e.ctrlKey) return

      this.on_draw_text_token(e)
    },
    search_in_google: function (e) {
      const selection = window.getSelection()
      const start_token_id = parseInt(selection.anchorNode.parentNode.id)
      let end_token_id;
      if (selection.focusNode.nodeName === "#text") {
        end_token_id = parseInt(selection.focusNode.parentNode.id)
      } else {
        end_token_id = parseInt(selection.focusNode.previousSibling.id)
      }
      if (!e.target.nodeName.includes('text') && start_token_id == end_token_id) {
        this.instance_in_progress = null
        return
      }
      let search_quiery = '';
      for (let i = start_token_id; i <= end_token_id; i++) {
        search_quiery += this.tokens.find(token => token.id === i).word;
        if (i < end_token_id) search_quiery += "+"
      }
      window.open(`https://www.google.com/search?q=${search_quiery}`, '_newtab');
      if (window.getSelection) {
        if (window.getSelection().empty) {  // Chrome
          window.getSelection().empty();
        } else if (window.getSelection().removeAllRanges) {  // Firefox
          window.getSelection().removeAllRanges();
        }
      } else if (document.selection) {  // IE?
        document.selection.empty();
      }

      this.annotation_ui_context.get_current_ann_ctx().search_mode = false
    },
    on_draw_text_token: function (e) {
      if (this.instance_in_progress && this.instance_in_progress.type === "relation" || !window.getSelection().anchorNode) return
      if (this.bulk_mode) return
      this.context_menu = null

      const selection = window.getSelection()
      const start_token_id = parseInt(selection.anchorNode.parentNode.id)
      let end_token_id;
      if (selection.focusNode.nodeName === "#text") {
        end_token_id = parseInt(selection.focusNode.parentNode.id)
      } else {
        end_token_id = parseInt(selection.focusNode.previousSibling.id)
      }
      if (!e.target.nodeName.includes('text') && start_token_id == end_token_id) {
        this.instance_in_progress = null
        return
      }

      this.on_select_text(start_token_id, end_token_id)
      this.remove_browser_selection()
    },
    on_select_text: function(start_token_id, end_token_id, direction = "right") {
      if (!start_token_id && start_token_id !== 0 || !end_token_id && end_token_id !== 0 ) return
      if (start_token_id < 0 || end_token_id > this.tokens[this.tokens.length - 1].id) return
      let start_token;
      while(!start_token) {
        start_token = this.tokens.find(token => token.id == start_token_id)
        if (!start_token && direction === "left") {
          start_token_id = start_token_id - 1
        } else if (!start_token && direction === 'right') {
          start_token_id = start_token_id + 1
        }
      }
      const draw_text = new DrawRects(this.tokens, this.lines, this.instance_list)
      const rects = draw_text.generate_selection_rect(start_token.id, end_token_id)
      this.on_start_draw_instance(start_token_id, end_token_id)
      this.selection_rects = rects
      this.show_label_selection = true
      this.selection_rects_next_token = null
    },
    on_mount: async function () {
      this.fetching_error = false
      let set_words;

      try {
        const {nltk: {words}} = await getTextService(this.working_file.text.tokens_url_signed)
        set_words = words

        this.initial_words_measures = set_words

        await this.initialize_instance_list()
        this.$emit('set_ui_schema')
      } catch(e) {
        this.fetching_error = true
      }
    },
    initialize_token_render: async function () {
      if (!this.$refs[`initial_svg_element_${this.working_file.id}`]) return
      if (!this.initial_words_measures) return

      const tokens = [];
      let token_x_position = 40;
      this.initial_words_measures.map((word, index) => {
        const refs = this.$refs[`word_${index}_file_${this.working_file.id}`]
        let current_token_width = 0
        if(refs && refs.length >  0){
          current_token_width = refs[0].getBoundingClientRect().width

        }
        if (this.lines.length === 0) {
          this.lines.push({id: 0, y: 5, initial_y: 5})
        }
        if (token_x_position + current_token_width > this.real_container_width) {
          this.lines.push({
            id: this.lines.length,
            y: this.lines[this.lines.length - 1].y + 40,
            initial_y: this.lines[this.lines.length - 1].y + 40
          })
          token_x_position = 40
        }
        if (word.value === '\n') {
          this.lines.push({
            id: this.lines.length,
            y: this.lines[this.lines.length - 1].y + 40,
            initial_y: this.lines[this.lines.length - 1].y + 40
          })
          token_x_position = 40
          return
        }

        const token = {
          id: index,
          word: word.value,
          tag: word.tag,
          width: current_token_width,
          start_x: word.tag !== 'word' ? token_x_position : token_x_position - 5,
          line: this.lines.length - 1
        }
        tokens.push(token)
        token_x_position = word.tag !== 'word' ? token_x_position + current_token_width + 5 : token_x_position + current_token_width
      })
      this.tokens = tokens
      this.image_annotation_ctx.rendering = false
      this.image_annotation_ctx.resizing = false

      if (this.annotation_ui_context.subtype === 'conversational') {
        setTimeout(() => {
          this.child_annotation_ctx_list.find(child => child.file.id === this.working_file.id).container_height = this.$refs[`text_annotation_area_${this.working_file.id}`].getBoundingClientRect().height + 25
        }, 100)
      }

    },
    // function to draw relations between instances
    on_trigger_instance_click: function (e, instance_id) {
      const context = e.ctrlKey && e.button === 0 || e.button === 2
      if (context) return

      if (this.bulk_mode) return this.bulk_labeling(instance_id)

      this.on_draw_relation(instance_id)
    },
    create_relation: function(label) {
      const relation_already_exists = this.instance_list.get().find(inst =>
        inst.type === "relation" &&
        inst.from_instance_id === this.instance_in_progress.start_instance &&
        inst.to_instance_id === this.instance_in_progress.end_instance &&
        !inst.soft_delete &&
        inst.label_file_id === label.id
      )
      if (this.instance_in_progress.start_instance !== this.instance_in_progress.end_instance && !relation_already_exists) {
        const created_instance = new TextRelationInstance();
        created_instance.create_frontend_instance(
          this.instance_in_progress.start_instance,
          this.instance_in_progress.end_instance,
          {...label}
        )
        this.instance_list.push([created_instance])

        //New command pattern
        const new_command = new CreateInstanceCommand([created_instance], this.instance_list)
        this.annotation_ui_context.command_manager.executeCommand(new_command)

        this.$emit('set_has_changed', true)
      }
      this.relation_drawing = false;
      this.instance_in_progress = null;
      this.show_label_selection = false
      this.path = {};
    },
    on_draw_relation: async function (instance_id) {
      const is_text_token = this.instance_list.get().find(instance => instance_id === instance.get_instance_data().id).type === "text_token"

      if (!is_text_token) return
      this.unselectable = true
      this.selection_rects = null
      this.show_label_selection = false

      if (!this.relation_drawing) {
        this.relation_drawing = true
        this.instance_in_progress = {
          id: this.instance_list.get().length,
          type: "relation",
          start_instance: instance_id,
          level: 0
        }
        window.addEventListener('mousemove', this.draw_relation_listener)
        return
      }

      this.unselectable = false
      this.instance_in_progress.end_instance = instance_id;

      this.show_label_selection = true
      window.removeEventListener('mousemove', this.draw_relation_listener)
    },
    draw_relation_listener: function (e) {
      this.path = {
        x: e.clientX,
        y: e.clientY
      }
    },
    //function to hover on instance
    on_instance_hover: function (instance_id) {
      const instance = this.instance_list.get().find(instance => instance.get_instance_data().id === instance_id)
      this.annotation_ui_context.get_current_ann_ctx().hover_instance = instance
    },
    on_instance_stop_hover: function () {
      this.annotation_ui_context.get_current_ann_ctx().hover_instance = null
    },
    // function to initialize drawing new instance
    on_start_draw_instance: function (start_token_id, end_token_id) {
      let end_token = this.tokens.find(token => token.id === end_token_id)

      if (!end_token) end_token = start_token_id
      else end_token = end_token_id

      this.instance_in_progress = {
        id: this.instance_list.get().length,
        type: "text_token",
        start_token: start_token_id,
        end_token: end_token,
        level: 0
      }
    },
    // function to finish drawing instance and remove selection
    on_finish_draw_instance: async function (label) {
      if (!this.instance_in_progress.start_token && this.instance_in_progress.start_token !== 0) return
      const instance_exists = this.instance_list.get().find(instance =>
        instance.start_token === this.instance_in_progress.start_token &&
        instance.end_token === this.instance_in_progress.end_token &&
        !instance.soft_delete &&
        instance.label_file_id === label.id
        ||
        instance.end_token === this.instance_in_progress.start_token &&
        instance.start_token === this.instance_in_progress.end_token &&
        !instance.soft_delete &&
        instance.label_file_id === label.id
      )
      if (!instance_exists) {
        const created_instance = new TextAnnotationInstance();
        created_instance.create_frontend_instance(
          this.instance_in_progress.start_token,
          this.instance_in_progress.end_token,
          {...label}
        )
        this.instance_list.push([created_instance])

        //New command pattern
        const new_command = new CreateInstanceCommand([created_instance], this.instance_list)
        this.annotation_ui_context.command_manager.executeCommand(new_command)
        this.$emit('set_has_changed', true)
      }
      // this.remove_browser_selection()
    },
    remove_browser_selection: function() {
      if (window.getSelection) {
        if (window.getSelection().empty) {
          window.getSelection().empty();
        } else if (window.getSelection().removeAllRanges) {
          window.getSelection().removeAllRanges();
        }
      } else if (document.selection) {
        document.selection.empty();
      }
    },
    on_popup_create_instance: function(label) {
      this.on_finish_draw_instance(label)
      this.selection_rects_next_token = this.instance_in_progress.end_token + 1
    },
    change_instance_label: async function (event) {
      const {instance, label} = event
      const new_command = new UpdateInstanceLabelCommand([instance], this.instance_list)
      new_command.set_new_label(label)
      this.annotation_ui_context.command_manager.executeCommand(new_command)
      this.$emit('set_has_changed', true)
    },
    delete_instance: async function (instance) {
      this.annotation_ui_context.get_current_ann_ctx().hover_instance = null

      if (this.annotation_ui_context.get_current_ann_ctx().current_instance && instance.creation_ref_id === this.annotation_ui_context.get_current_ann_ctx().current_instance.creation_ref_id) {
        this.annotation_ui_context.get_current_ann_ctx().current_instance = null
      }

      const new_delete_command = new DeleteInstanceCommand([instance], this.instance_list)
      this.annotation_ui_context.command_manager.executeCommand(new_delete_command)
      this.$emit('set_has_changed', true)
      this.context_menu = null
    },
    change_label_visibility: async function (label) {
      if (label.is_visible) {
        this.invisible_labels = this.invisible_labels.filter(label_id => label_id !== label.id)
      } else {
        this.invisible_labels.push(label.id)
      }
    },
    initialize_instance_list: async function () {
      let url;
      let payload;
      this.current_global_instance = null // reset
      if (this.task && this.task.id) {
        url = `/api/v1/task/${this.task.id}/annotation/list`;
        payload = {
          directory_id: this.$store.state.project.current_directory.directory_id,
          job_id: this.job_id,
          task_child_file_id: this.working_file.id,
          attached_to_job: this.working_file.attached_to_job,
        }
      } else {
        url = `/api/project/${this.project_string_id}/file/${this.working_file.id}/annotation/list`;
        payload = {}
      }
      let instance_list = await getInstanceList(url, payload)

      instance_list = this.get_and_set_global_instance(instance_list)


      // New command pattern
      this.instance_list = new InstanceList(instance_list)
    },
    after_save: async function (updated_instances) {
      updated_instances.map(add_instance => {
        if (add_instance.type === "global") return

        const old_instance = this.instance_list.get_all().find(instance => instance.creation_ref_id === add_instance.creation_ref_id)
        const old_id = old_instance.get_instance_data().id

        this.instance_list.get_all().find(instance => instance.creation_ref_id === add_instance.creation_ref_id).id = add_instance.id
        if (this.instance_in_progress) {
          this.instance_in_progress.start_instance = this.instance_in_progress.start_instance === old_id ? add_instance.id : this.instance_in_progress.start_instance
        }

        this.instance_list.get_all()
          .filter(instance => {
            const {from_instance_id, to_instance_id} = instance.get_instance_data()
            return instance.type === "relation" && (from_instance_id === old_id || to_instance_id === old_id)
          })
          .map(instance => {
            const {from_instance_id} = instance.get_instance_data()
            if (from_instance_id === old_id) instance.from_instance_id = add_instance.id
            else instance.to_instance_id = add_instance.id
          })
        })
    },
    // Find intersection and update level of the instance
    find_intersections: function (rects_to_draw) {
      rects_to_draw.map((rect, index) => {
        rects_to_draw.map((comp_rect, comp_index) => {
          if (index === comp_index) return
          if (rect.line !== comp_rect.line) return
          if (rect.x <= comp_rect.x && rect.x + rect.width > comp_rect.x && rect.y === comp_rect.y) {
            if (rect.width === comp_rect.width) {
              if (comp_rect.instance_type === "relation") return comp_rect.y = comp_rect.y - this.additional_line_space
              else {
                return rect.y = rect.y - this.additional_line_space
              }
            }
            if (rect.width > comp_rect.width) return rect.y = rect.y - this.additional_line_space
            comp_rect.y = comp_rect.y - this.additional_line_space
            this.find_intersections(rects_to_draw)
          }
        })
      })
      rects_to_draw.map((rect, index) => {
        rects_to_draw.map((comp_rect, comp_index) => {
          if (index === comp_index) return
          if (rect.line !== comp_rect.line) return
          if (rect.x <= comp_rect.x && rect.x + rect.width > comp_rect.x && rect.y === comp_rect.y) {
            if (rect.width === comp_rect.width) {
              if (comp_rect.instance_type === "relation") return comp_rect.y = comp_rect.y - this.additional_line_space
              else {
                return rect.y = rect.y - this.additional_line_space
              }
            }
            if (rect.width > comp_rect.width) return rect.y = rect.y - this.additional_line_space
            comp_rect.y = comp_rect.y - this.additional_line_space
            this.find_intersections(rects_to_draw)
          }
        })
      })

      const rects_lines_map = rects_to_draw.reduce(
        (entryMap, e) => entryMap.set(e.line, [...entryMap.get(e.line) || [], e]),
        new Map()
      )

      this.lines.forEach(line => line.y = line.initial_y)

      this.lines.map(line => {
        if (rects_lines_map.get(line.id)) {
          const rect_levels = [...rects_lines_map.get(line.id).map(rect => rect.y)]
          const move_strings_level = (Math.max(...rect_levels) - Math.min(...rect_levels)) / this.additional_line_space
          this.update_line_height(line.id, move_strings_level)
        }
      })
    },
    // Update line height if there are few levels of instances
    update_line_height: function (line_id, level) {
      this.lines.map(line => {
        if (line.id >= line_id) {
          line.y = line.y + level * this.additional_line_space
        }
      })
    },
    // draw_instance - is only returning rects that have to be drawn
    draw_instance: function (instance) {
      const draw_class = new DrawRects(this.tokens, this.lines, this.instance_list);
      const drawn_rects = draw_class.generate_rects_from_instance(instance)
      return drawn_rects
    },
    // this is function to check what direction relation arrow should piint to
    insatance_orientation_direct: function (relational_instance) {
      const start_instance = this.instance_list.get().find(find_instance => find_instance.get_instance_data().id === relational_instance.get_instance_data().from_instance_id)
      const starting_token = this.tokens.find(token => token.id === start_instance.start_token)
      const end_instance = this.instance_list.get().find(find_instance => find_instance.get_instance_data().id === relational_instance.get_instance_data().to_instance_id)
      const end_token = this.tokens.find(token => token.id === end_instance.end_token)
      return starting_token.id < end_token.id
    },
    on_select_instance: function(instance) {
      this.annotation_ui_context.get_current_ann_ctx().current_instance = instance
    },
    update_attribute: function(event, is_global) {
      const attribute = event
      let command

      const global_instance = this.annotation_ui_context.instance_store.instance_store[this.working_file.id].global_instance

      if (is_global) {
        command = new UpdateGlobalAttributeCommand([global_instance], this.instance_list, true)
      } else {
        command = new UpdateInstanceAttributeCommand([this.instance_list.get().find(inst => inst.creation_ref_id === this.annotation_ui_context.get_current_ann_ctx().current_instance.creation_ref_id)], this.instance_list)
      }

      let attribute_to_pass

      if (["slider", "text", "time", "date"].includes(attribute[0].kind)) attribute_to_pass = attribute[1]
      else if (Array.isArray(attribute[1])) attribute_to_pass = [...attribute[1]]
      else attribute_to_pass = {...attribute[1]}

      command.set_new_attribute(attribute[0].id, attribute_to_pass)
      this.annotation_ui_context.command_manager.executeCommand(command)
      this.$emit('set_has_changed', true)
    },
    get_and_set_global_instance: function (instance_list) {
      if(!this.global_attribute_groups_list){
        return instance_list
      }
      if(this.global_attribute_groups_list.length === 0){
        return instance_list
      }
      let existing_global_instance = instance_list.find(inst => inst.type === 'global');
      if(existing_global_instance){
        this.current_global_instance = existing_global_instance;
      }
      else{
        this.current_global_instance = this.new_global_instance();
        instance_list.push(this.current_global_instance)
      }

      return instance_list

    },
    new_global_instance: function () {

      let new_instance = new Instance();
      new_instance.type = 'global'
      new_instance.creation_ref_id = uuidv4();
      return new_instance

    },
  }
})
</script>


<style scoped>
.unselectable {
  -moz-user-select: -moz-none;
  -khtml-user-select: none;
  -webkit-user-select: none;

  /*
    Introduced in IE 10.
    See http://ie.microsoft.com/testdrive/HTML5/msUserSelect/
  */
  -ms-user-select: none;
  user-select: none;
}
</style>
