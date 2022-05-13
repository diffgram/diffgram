<template>
  <div style="display: flex; flex-direction: column">
    <div style="position: relative">
      <main_menu
        :height="`${!task ? '100px' : '50px'}`"
        :show_default_navigation="!task"
      >
        <template slot="second_row">
          <text_toolbar
            :undo_disabled="undo_disabled"
            :redo_disabled="redo_disabled"
            :has_changed="has_changed"
            :label_schema="label_schema"
            :save_loading="save_loading"
            :loading="rendering"
            :project_string_id="project_string_id"
            :label_list="label_list"
            :label_file_colour_map="label_file_colour_map"
            :task="task"
            :file="file"
            :search_mode="search_mode"
            :bulk_mode="bulk_label"
            @change_label_schema="on_change_label_schema"
            @on_task_annotation_complete_and_save="on_task_annotation_complete_and_save"
            @task_update_toggle_deferred="defer_task"
            @change_label_file="change_label_file"
            @change_label_visibility="change_label_visibility"
            @change_file="change_file"
            @save="save"
            @change_task="trigger_task_change"
            @undo="undo()"
            @redo="redo()"
          />
        </template>
      </main_menu>
    </div>
    <div style="display: flex; flex-direction: row">
      <text_sidebar
        :instance_list="new_instance_list ? new_instance_list.get().filter(instance => !instance.soft_delete) : []"
        :label_list="label_list"
        :loading="rendering"
        :label_file_colour_map="label_file_colour_map"
        :toolbar_height="`${!task ? '100px' : '50px'}`"
        :project_string_id="project_string_id"
        :schema_id="label_schema.id"
        :current_instance="current_instance"
        :attribute_group_list_prop="label_list"
        :per_instance_attribute_groups_list="per_instance_attribute_groups_list"
        @on_select_instance="on_select_instance"
        @delete_instance="delete_instance"
        @on_instance_hover="on_instance_hover"
        @on_instance_stop_hover="on_instance_stop_hover"
        @on_update_attribute="on_update_attribute"
        @change_instance_label="change_instance_label"
      />
      <text_fast_label 
        v-if="show_label_selection"
        :rects="selection_rects"
        :arrow_position="render_drawing_arrow && render_drawing_arrow.arrow ? render_drawing_arrow.arrow : null"
        :label_list="label_list"
        @create_instance="on_popup_create_instance"
        @create_relation="create_relation"
        @remove_listeners="remove_hotkeys_listeners"
        @add_listeners="add_hotkeys_listeners"
      />
      <text_context_menu
        v-if="context_menu"
        :context_menu="context_menu"
        @delete_instance="delete_instance"
      />
      <svg
        ref="initial_svg_element"
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
        direction="ltr"
        id="svg0:60"
        @mouseup="trigger_mouseup"
        :style="`height: ${lines && lines.length > 0 ? lines[lines.length - 1].y + 60 : 10}px; width: ${text_field_width}`"
        :class="unselectable && 'unselectable'"
      >
        <g v-if="rendering" transform="translate(0, 23.5)">
          <text
            v-for="(word, index) in initial_words_measures"
            :key="word.value + index"
            :ref="`word_${index}`"
            x="40"
            y="5"
            fill="white"
            text-anchor="middle">
            {{ word.value }}
          </text>
          <text x="40">Loading...</text>
        </g>
        <g v-if="resizing" transform="translate(0, 23.5)">
          <text
            v-for="(word, index) in initial_words_measures"
            :key="word.value + index"
            :ref="`word_${index}`"
            x="40"
            y="5"
            fill="white"
            text-anchor="middle">
            {{ word.value }}
          </text>
          <text x="40">Resizing...</text>
        </g>
        <g ref="main-text-container" transform="translate(0, 23.5)" v-else>
          <relation_in_progress 
            v-if="relation_drawing"
            :render_drawing_arrow="render_drawing_arrow"
          />
          <g v-if="render_rects.length > 0">
            <rect
              v-for="instance in new_instance_list.get().filter(instance => !instance.soft_delete && !invisible_labels.includes(instance.label_file_id))"
              :key="`instance_rect_${instance.get_instance_data().id}`"
              :x="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x"
              :y="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y - 15"
              :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'rgba(255, 0, 0, 0.2)' : `rgba(${instance.label_file.colour.rgba.r}, ${instance.label_file.colour.rgba.g}, ${instance.label_file.colour.rgba.b}, 0.2)`"
              :width="instance.label_file.label.name.length * 8"
              :height="15"
              @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
              @mousedown="(e) => on_trigger_instance_click(e, instance.get_instance_data().id)"
              @mouseleave="on_instance_stop_hover"
              @contextmenu="(e) => on_open_context_menu(e, instance)"
              style="font-size: 10px; cursor: pointer"
              class="unselectable"
            />
            <text
              v-for="instance in new_instance_list.get().filter(instance => !instance.soft_delete && !invisible_labels.includes(instance.label_file_id))"
              :key="`instance_${instance.get_instance_data().id}`"
              :x="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x + 2"
              :y="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y - 3"
              :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
              @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
              @mousedown="(e) => on_trigger_instance_click(e, instance.get_instance_data().id)"
              @mouseleave="on_instance_stop_hover"
              @contextmenu="(e) => on_open_context_menu(e, instance)"
              style="font-size: 10px; cursor: pointer;"
              class="unselectable"
            >
              {{ instance.label_file.label.name }}
            </text>
            <rect
              v-for="instance in new_instance_list.get().filter(instance => !instance.soft_delete && instance.type === 'relation' && !invisible_labels.includes(instance.label_file_id))"
              :key="`rel_start_${instance.get_instance_data().id}`"
              :x="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x"
              :y="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y"
              :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
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
              v-for="instance in new_instance_list.get().filter(instance => !instance.soft_delete && instance.type === 'relation' && !invisible_labels.includes(instance.label_file_id))"
              :key="`rel_start_marker_${instance.get_instance_data().id}`"
              :cx="insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).x + render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).width"
              :cy="insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y + 10 : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).y + 10"
              :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
              r="2"
              class="unselectable"
            />
            <rect
              v-for="instance in new_instance_list.get().filter(instance => !instance.soft_delete && instance.type === 'relation' && !invisible_labels.includes(instance.label_file_id))"
              :key="`rel_end_${instance.get_instance_data().id}`"
              :x="render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).x + render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).width"
              :y="render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).y"
              :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
              :width="1"
              :height="10"
              @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
              @mousedown="(e) => on_trigger_instance_click(e, instance.get_instance_data().id)"
              @mouseleave="on_instance_stop_hover"
              style="font-size: 10px; cursor: pointer"
              class="unselectable"
            />
            <path
              v-for="instance in new_instance_list.get().filter(instance => !instance.soft_delete && instance.type === 'relation' && !invisible_labels.includes(instance.label_file_id))"
              :key="`rel_end_marker_${instance.get_instance_data().id}`"
              :d="`M ${!insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).x + render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).width} ${!insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y + 10 : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).y + 10} l -5, -5 l 10, 0 l -5, 5`"
              :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
              class="unselectable"
            />
            <rect
              v-for="rect in render_rects"
              :key="`rect_x_${rect.x}_y_${rect.y}_width_${rect.width}`"
              :fill="hover_instance && (hover_instance.get_instance_data().id === rect.instance_id || hover_instance.from_instance_id === rect.instance_id || hover_instance.to_instance_id === rect.instance_id) ? 'red' : rect.color"
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
              :x="token.start_x"
              :fill="hover_instance &&
                            (
                                (hover_instance.start_token <= token.id && token.id <= hover_instance.end_token) ||
                                (hover_instance.start_token >= token.id && token.id >= hover_instance.end_token)
                            ) ? 'red' : 'black'"
            >
              {{ token.word }}
            </text>
          </g>
          <text_selection_svg 
            v-if="selection_rects"
            :rects="selection_rects" 
            @on_change_selection_border="on_change_selection_border"
            @on_start_moving_borders="on_start_moving_borders"
          />
        </g>
      </svg>
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
import {CommandManagerAnnotationCore} from "../annotation/annotation_core_command_manager"
import {CreateInstanceCommand as CreateInstanceCommandLegacy} from "../annotation/commands/create_instance_command";
import {TextAnnotationInstance, TextRelationInstance} from "../vue_canvas/instances/TextInstance"
import {postInstanceList, getInstanceList} from "../../services/instanceList"
import getTextService from "../../services/getTextService"
import {deferTask, finishTaskAnnotation} from "../../services/tasksServices"
// New command pattern
import CommandManager from "../../helpers/command/command_manager"
import InstanceList from "../../helpers/instance_list"
import History from "../../helpers/history"
import {
  CreateInstanceCommand,
  DeleteInstanceCommand,
  UpdateInstanceLabelCommand,
  UpdateInstanceAttributeCommand
} from "../../helpers/command/available_commands"
import DrawRects from "./text_utils/draw_rects";
import closest_token from "./text_utils/closest_token"

export default Vue.extend({
  name: "text_token_core",
  components: {
    text_toolbar,
    text_sidebar,
    text_selection_svg,
    text_fast_label,
    text_context_menu,
    relation_in_progress
  },
  props: {
    file: {
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
    }
  },
  data() {
    return {
      text: null,
      current_label: null,
      rendering: true,
      resizing: false,
      relation_drawing: false,
      initial_words_measures: [],
      lines: [],
      tokens: [],
      instance_list: [],
      invisible_labels: [],
      current_instance: null,
      //Modes
      search_mode: false,
      bulk_label: false,
      //effects
      hover_instance: null,
      //Helpers
      instance_in_progress: null,
      path: {},
      //Render constants
      additional_line_space: 30,
      show_default_navigation: true,
      unselectable: false,
      text_field_heigth: 100,
      text_field_width: '100%',
      re_render_func: undefined,
      selection_rects: null,
      show_label_selection: false,
      moving_border: false,
      context_menu: null,
      // Command
      command_manager: undefined,
      has_changed: false,
      save_loading: false,
      // New command pattern
      new_instance_list: undefined,
      new_command_manager: undefined,
      new_history: undefined,
    }
  },
  mounted() {
    this.on_unload_listener()
    this.remove_hotkeys_listeners()
    this.add_hotkeys_listeners()
    this.on_mount()
    this.start_autosave()

    window.addEventListener("keyup", this.key_up_unremovable_listeners)
  },
  computed: {
    render_rects: function () {
      if (this.rendering || this.resizing) return [];
      if (this.tokens.length === 0) return [];

      let rects_to_draw = [];
      this.new_instance_list.get().filter(instance => !instance.soft_delete && !this.invisible_labels.includes(instance.label_file_id)).map(instance => {
        const instance_rects = this.draw_instance(instance)
        rects_to_draw = [...rects_to_draw, ...instance_rects]
      })

      this.find_intersections(rects_to_draw)
      rects_to_draw = [];
      this.new_instance_list.get().filter(instance => !instance.soft_delete && !this.invisible_labels.includes(instance.label_file_id)).map(instance => {
        const instance_rects = this.draw_instance(instance)
        rects_to_draw = [...rects_to_draw, ...instance_rects]
      })
      this.find_intersections(rects_to_draw)
      return rects_to_draw
    },
    render_drawing_arrow: function () {
      if (!this.instance_in_progress) return {}
      const scroll_y = window.pageYOffset || document.documentElement.scrollTop
      const inst = this.render_rects.find(rect => rect.instance_id === this.instance_in_progress.start_instance)
      
      if (!inst) return {}
      const {x, y} = inst

      const top_offset = this.task && this.task.id ? 50 : 100

      if (this.path.x && this.path.y) {
        return {
          marker: {
            x,
            y
          },
          arrow: {
            x: this.path.x - 350,
            y: this.path.y - top_offset + scroll_y - 23.5 + 5
          },
          path: `M ${x} ${y} Q ${this.path.x - 350 - 100} ${this.path.y - top_offset + scroll_y - 23.5 - 30} ${this.path.x - 350} ${this.path.y - top_offset + scroll_y - 23.5}`
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
      return !this.new_history || !this.new_history.undo_posible
    },
    redo_disabled: function () {
      return !this.new_history || !this.new_history.redo_posible
    }
  },
  watch: {
    file: function () {
      this.rendering = true
      this.instance_list = [];
      this.text = null;
      this.command_manager = null;
      this.initial_words_measures = [];
      this.lines = []
      this.on_mount()
    },
    task: function () {
      this.rendering = true
      this.instance_list = [];
      this.text = null;
      this.command_manager = null;
      this.initial_words_measures = [];
      this.lines = []
      this.on_mount()
    }
  },
  methods: {
    on_start_moving_borders: function() {
      this.show_label_selection = false
      this.moving_border = true
    },
    on_change_selection_border: function(start_coordinates, end_coordinates) {
      const draw_class = new DrawRects(this.tokens, this.lines, this.new_instance_list)
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
      this.context_menu = {
        x: e.clientX,
        y: e.clientY - 85,
        instance
      }
      this.current_instance = instance
    },
    on_change_label_schema: function(schema){
      this.$emit('change_label_schema', schema)
    },
    on_task_annotation_complete_and_save: async function () {
      await this.save();
      await this.save();
      const response = await finishTaskAnnotation(this.task.id);
      const new_status = response.data.task.status;
      this.task.status = new_status;
      if (new_status !== "complete") {
        this.submitted_to_review = true;
      }
      if (this.$props.task && this.$props.task.id) {
        this.save_loading_image = false;
        this.trigger_task_change("next", this.$props.task, true);
      }
    },
    defer_task: async function () {
      const defered = await deferTask({
        task_id: this.task.id,
        mode: "toggle_deferred"
      })
      this.trigger_task_change('next')
    },
    bulk_labeling: function (instance_id) {
      const instance = this.new_instance_list.get().find(inst => {
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
      const working_insatnce_list = this.new_instance_list.get().filter(inst => inst.type === "text_token")
      same_token_indexes.map(index => {
        const instance_already_exists = working_insatnce_list.find(inst => inst.start_token === index && inst.end_token === index)
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
        this.new_instance_list.push(newly_created_instances)
        const new_command = new CreateInstanceCommand(newly_created_instances, this.new_instance_list)
        this.new_command_manager.executeCommand(new_command)

        this.has_changed = true
      }
    },
    trigger_task_change: async function (direction, assign_to_user = false) {
      if (this.has_changed) {
        await this.save();
        await this.save();
      }
      this.$emit("request_new_task", direction, this.task, assign_to_user);
    },
    remove_hotkeys_listeners: function() {
      window.removeEventListener("keydown", this.keydown_event_listeners)
      window.removeEventListener("keyup", this.keyup_event_listeners)
    },
    add_hotkeys_listeners: function() {
      window.addEventListener("keydown", this.keydown_event_listeners)
      window.addEventListener("keyup", this.keyup_event_listeners)
    },
    on_unload_listener: function () {
      window.addEventListener("beforeunload", this.leave_listener);
      window.addEventListener("resize", this.resize_listener)
    },
    resize_listener: function () {
      this.resizing = true
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
      if (e.keyCode === 83) {
        await this.save();
        await this.save();
      } else if (e.keyCode === 71 && !this.search_mode) {
        this.search_mode = true;
      } else if (e.keyCode === 66 && !this.bulk_label) {
        this.bulk_label = true;
      }
    },
    keyup_event_listeners: function (e) {
      if (e.keyCode === 71) {
        this.search_mode = false;
      } else if (e.keyCode === 66) {
        this.bulk_label = false;
      }
    },
    key_up_unremovable_listeners: function(e) {
      if (e.keyCode === 27) {
        this.current_instance = null
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
        this.on_select_text(this.selection_rects[0].end_token_id + 1, this.selection_rects[0].end_token_id + 1)
      }
    },
    start_autosave: function () {
      this.interval_autosave = setInterval(
        this.detect_is_ok_to_save,
        15 * 1000
      );
    },
    detect_is_ok_to_save: async function () {
      if (this.has_changed && !this.instance_in_progress) {
        await this.save();
        await this.save();
      }
    },
    trigger_mouseup: function (e) {
      if (this.search_mode) return this.search_in_google(e)
      if (this.selection_rects && !e.target.nodeName.includes('text')) return;
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
        search_quiery += this.tokens[i].word;
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
      this.search_mode = false
    },
    on_draw_text_token: function (e) {
      if (this.instance_in_progress && this.instance_in_progress.type === "relation" || !window.getSelection().anchorNode) return
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
      if (start_token_id < 0 || end_token_id > this.tokens.length + 1) return
      
      let start_token;
      while(!start_token) {
        start_token = this.tokens.find(token => token.id == start_token_id)
        if (!start_token && direction === "left") {
          start_token_id = start_token_id - 1
        } else if (!start_token && direction === 'right') {
          start_token_id = start_token_id + 1
        }
      }
      const draw_text = new DrawRects(this.tokens, this.lines, this.new_instance_list)
      const rects = draw_text.generate_selection_rect(start_token.id, end_token_id)
      this.on_start_draw_instance(start_token_id, end_token_id)
      this.selection_rects = rects
      this.show_label_selection = true
    },
    on_mount: async function () {
      let set_words;
      if (this.task) {
        const {nltk: {words}} = await getTextService(this.task.file.text.tokens_url_signed)
        set_words = words
      } else {
        const {nltk: {words}} = await getTextService(this.file.text.tokens_url_signed)
        set_words = words
      }
      this.command_manager = new CommandManagerAnnotationCore()
      // New command pattern
      this.new_history = new History()
      this.new_command_manager = new CommandManager(this.new_history)

      this.initial_words_measures = set_words
      setTimeout(() => this.initialize_token_render(), 1000)
      this.initialize_instance_list()
    },
    initialize_token_render: async function () {
      const fixed_svg_width = this.$refs.initial_svg_element.clientWidth;
      const tokens = [];
      let token_x_position = 40;

      this.initial_words_measures.map((word, index) => {
        const current_token_width = this.$refs[`word_${index}`][0].getBoundingClientRect().width

        if (this.lines.length === 0) {
          this.lines.push({id: 0, y: 5, initial_y: 5})
        }
        if (token_x_position + current_token_width > fixed_svg_width) {
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
      this.rendering = false
      this.resizing = false
    },
    change_label_file: function (event) {
      this.current_label = event
    },
    // function to draw relations between instances
    on_trigger_instance_click: function (e, instance_id) {
      const context = e.ctrlKey && e.button === 0 || e.button === 2
      if (context) return
      
      if (this.bulk_label) return this.bulk_labeling(instance_id)
      this.on_draw_relation(instance_id)
    },
    create_relation: function(label) {
      const relation_already_exists = this.new_instance_list.get().find(inst =>
        inst.type === "relation" &&
        inst.from_instance_id === this.instance_in_progress.start_instance &&
        inst.to_instance_id === this.instance_in_progress.end_instance &&
        !inst.soft_delete
      )
      if (this.instance_in_progress.start_instance !== this.instance_in_progress.end_instance && !relation_already_exists) {
        const created_instance = new TextRelationInstance();
        created_instance.create_frontend_instance(
          this.instance_in_progress.start_instance,
          this.instance_in_progress.end_instance,
          {...label}
        )
        this.new_instance_list.push([created_instance])
        const command = new CreateInstanceCommandLegacy(created_instance, this)
        this.command_manager.executeCommand(command)

        //New command pattern
        const new_command = new CreateInstanceCommand([created_instance], this.new_instance_list)
        this.new_command_manager.executeCommand(new_command)

        this.has_changed = true
      }
      this.relation_drawing = false;
      this.instance_in_progress = null;
      this.show_label_selection = false
      this.path = {};
    },
    on_draw_relation: async function (instance_id) {
      const is_text_token = this.new_instance_list.get().find(instance => instance_id === instance.get_instance_data().id).type === "text_token"

      if (!is_text_token) return
      this.unselectable = true
      this.selection_rects = null
      this.show_label_selection = false

      if (!this.relation_drawing) {
        this.relation_drawing = true
        this.instance_in_progress = {
          id: this.new_instance_list.get().length,
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
      const instance = this.new_instance_list.get().find(instance => instance.get_instance_data().id === instance_id)
      this.hover_instance = instance
    },
    on_instance_stop_hover: function () {
      this.hover_instance = null
    },
    // function to initialize drawing new instance
    on_start_draw_instance: function (start_token_id, end_token_id) {
      let end_token = this.tokens.find(token => token.id === end_token_id)

      if (!end_token) end_token = start_token_id
      else end_token = end_token_id

      this.instance_in_progress = {
        id: this.new_instance_list.get().length,
        type: "text_token",
        start_token: start_token_id,
        end_token: end_token,
        level: 0
      }
    },
    // function to finish drawing instance and remove selection
    on_finish_draw_instance: async function (label) {
      if (!this.instance_in_progress.start_token && this.instance_in_progress.start_token !== 0) return
      const instance_exists = this.new_instance_list.get().find(instance =>
        instance.start_token === this.instance_in_progress.start_token && instance.end_token === this.instance_in_progress.end_token && !instance.soft_delete
        ||
        instance.end_token === this.instance_in_progress.start_token && instance.start_token === this.instance_in_progress.end_token && !instance.soft_delete
      )
      if (!instance_exists) {
        const created_instance = new TextAnnotationInstance();
        created_instance.create_frontend_instance(
          this.instance_in_progress.start_token,
          this.instance_in_progress.end_token,
          {...label}
        )
        this.new_instance_list.push([created_instance])
        const command = new CreateInstanceCommandLegacy(created_instance, this)
        this.command_manager.executeCommand(command)

        //New command pattern
        const new_command = new CreateInstanceCommand([created_instance], this.new_instance_list)
        this.new_command_manager.executeCommand(new_command)
        this.has_changed = true
      }
      this.remove_browser_selection()
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
      this.on_select_text(this.instance_in_progress.end_token + 1, this.instance_in_progress.end_token + 1)
    },
    change_instance_label: async function (event) {
      const {instance, label} = event
      const new_command = new UpdateInstanceLabelCommand([instance], this.new_instance_list)
      new_command.set_new_label(label)
      this.new_command_manager.executeCommand(new_command)
      this.has_changed = true
    },
    delete_instance: async function (instance) {
      this.hover_instance = null
      if (this.current_instance && instance.creation_ref_id === this.current_instance.creation_ref_id) {
        this.current_instance = null
      }
      const new_delete_command = new DeleteInstanceCommand([instance], this.new_instance_list)
      this.new_command_manager.executeCommand(new_delete_command)
      this.has_changed = true
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
      if (this.task && this.task.id) {
        url = `/api/v1/task/${this.task.id}/annotation/list`;
        payload = {
          directory_id: this.$store.state.project.current_directory.directory_id,
          job_id: this.job_id,
          attached_to_job: this.task.file.attached_to_job,
        }
      } else {
        url = `/api/project/${this.$props.project_string_id}/file/${this.$props.file.id}/annotation/list`;
        payload = {}
      }
      const instance_list = await getInstanceList(url, payload)
      // New command patterm
      this.new_instance_list = new InstanceList(instance_list)
    },
    save: async function () {
      this.has_changed = false
      this.save_loading = true
      let url;
      if (this.task && this.task.id) {
        url = `/api/v1/task/${this.task.id}/annotation/update`;
      } else {
        url = `/api/project/${this.project_string_id}/file/${this.file.id}/annotation/update`
      }
      if (!this.instance_in_progress) {
        const res = await postInstanceList(url, this.new_instance_list.get_all())
        const {added_instances} = res
        added_instances.map(add_insatnce => {
          const old_instance = this.new_instance_list.get_all().find(instance => instance.creation_ref_id === add_insatnce.creation_ref_id)
          const old_id = old_instance.get_instance_data().id
          this.new_instance_list.get_all().find(instance => instance.creation_ref_id === add_insatnce.creation_ref_id).id = add_insatnce.id
          if (this.instance_in_progress) {
            this.instance_in_progress.start_instance = this.instance_in_progress.start_instance === old_id ? add_insatnce.id : this.instance_in_progress.start_instance
          }
          this.new_instance_list.get_all()
            .filter(instance => {
              const {from_instance_id, to_instance_id} = instance.get_instance_data()
              return instance.type === "relation" && (from_instance_id === old_id || to_instance_id === old_id)
            })
            .map(instance => {
              const {from_instance_id} = instance.get_instance_data()
              if (from_instance_id === old_id) instance.from_instance_id = add_insatnce.id
              else instance.to_instance_id = add_insatnce.id
            })
        })
      }
      this.save_loading = false
    },
    undo: function () {
      if (!this.new_history.undo_posible) return;

      let undone = this.new_command_manager.undo();
      this.current_instance = null

      if (undone) this.has_changed = true;
    },
    redo: function () {
      if (!this.new_history.redo_posible) return;

      let redone = this.new_command_manager.redo();
      this.current_instance = null

      if (redone) this.has_changed = true;
    },
    change_file(direction, file) {
      if (direction == "next" || direction == "previous") {
        this.$emit("request_file_change", direction, file);
      }
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
      const draw_class = new DrawRects(this.tokens, this.lines, this.new_instance_list);
      const drawn_rects = draw_class.generate_rects_from_instance(instance)
      return drawn_rects
    },
    // this is function to check what direction relation arrow should piint to
    insatance_orientation_direct: function (relational_instance) {
      const start_instance = this.new_instance_list.get().find(find_instance => find_instance.get_instance_data().id === relational_instance.get_instance_data().from_instance_id)
      const starting_token = this.tokens.find(token => token.id === start_instance.start_token)
      const end_instance = this.new_instance_list.get().find(find_instance => find_instance.get_instance_data().id === relational_instance.get_instance_data().to_instance_id)
      const end_token = this.tokens.find(token => token.id === end_instance.end_token)
      return starting_token.id < end_token.id
    },
    on_select_instance: function(instance) {
      this.current_instance = instance
    },
    on_update_attribute: function(attribute) {
      const command = new UpdateInstanceAttributeCommand([this.new_instance_list.get().find(inst => inst.creation_ref_id === this.current_instance.creation_ref_id)], this.new_instance_list)
      command.set_new_attribute(attribute[0].id, {...attribute[1]})
      this.new_command_manager.executeCommand(command)
      this.has_changed = true
    }
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
