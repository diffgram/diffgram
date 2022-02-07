<template>
<div style="display: flex; flex-direction: column">
    <div style="position: relative">
      <main_menu
        :height="`${show_default_navigation ? '100px' : '50px'}`"
        :show_default_navigation="show_default_navigation"
      >
        <template slot="second_row">
            <text_toolbar
                :undo_disabled="undo_disabled"
                :redo_disabled="redo_disabled"
                :has_changed="has_changed"
                :save_loading="save_loading"
                @change_label_file="change_label_file"
                @change_label_visibility="change_label_visibility"
                @change_file="change_file"
                @undo="undo()"
                @redo="redo()"
            />
        </template>
      </main_menu>
    </div>
    <div style="display: flex; flex-direction: row">
        <text_sidebar 
            :instance_list="instance_list.filter(instance => !instance.soft_delete)"
            :label_list="label_list"
            :loading="rendering"
            @delete_instance="delete_instance"
            @on_instance_hover="on_instance_hover"
            @on_instance_stop_hover="on_instance_stop_hover"
            @change_instance_label="change_instance_label"
        />
        <svg 
            ref="initial_svg_element" 
            version="1.1" 
            xmlns="http://www.w3.org/2000/svg" 
            direction="ltr" 
            id="svg0:60" 
            width="100%" 
            :style="`height: 5000px`"
            @mouseup="on_draw_text_token"
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
            <g ref="main-text-container" v-else>
                <g
                    v-if="relation_drawing"
                >
                    <circle 
                        :cx="render_drawing_arrow.marker.x" 
                        :cy="render_drawing_arrow.marker.y" 
                        :fill="current_label.colour.hex"
                        r="3" 
                    />
                    <path
                        :stroke="current_label.colour.hex" 
                        :d="render_drawing_arrow.path" 
                        fill="transparent"
                    />
                    <path 
                        :d="`M ${render_drawing_arrow.arrow.x} ${render_drawing_arrow.arrow.y} l -5, -5 l 10, 0 l -5, 5`" 
                        :fill="current_label.colour.hex"
                    />
                </g>
                <text 
                    v-for="instance in instance_list.filter(instance => !instance.soft_delete && !invisible_labels.includes(instance.label_file_id))"
                    :key="`instance_${instance.get_instance_data().id}`"
                    :x="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x" 
                    :y="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y - 3"
                    :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                    @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
                    @mousedown="() => on_draw_relation(instance.get_instance_data().id)"
                    @mouseleave="on_instance_stop_hover"
                    style="font-size: 10px; cursor: pointer"
                >
                    {{ instance.label_file.label.name }}
                </text>
                <rect 
                    v-for="instance in instance_list.filter(instance => !instance.soft_delete && instance.type === 'relation' && !invisible_labels.includes(instance.label_file_id))"
                    :key="`rel_start_${instance.get_instance_data().id}`"
                    :x="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x" 
                    :y="render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y"
                    :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                    :width="1"
                    :height="10"
                    @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
                    @mousedown="() => on_draw_relation(instance.get_instance_data().id)"
                    @mouseleave="on_instance_stop_hover"
                    style="font-size: 10px; cursor: pointer"
                />
                <circle 
                    v-for="instance in instance_list.filter(instance => !instance.soft_delete && instance.type === 'relation' && !invisible_labels.includes(instance.label_file_id))"
                    :key="`rel_start_marker_${instance.id}`"
                    :cx="insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).x + render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).width" 
                    :cy="insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y + 10 : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).y + 10" 
                    :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                    r="2" 
                />
                <rect 
                    v-for="instance in instance_list.filter(instance => !instance.soft_delete && instance.type === 'relation' && !invisible_labels.includes(instance.label_file_id))"
                    :key="`rel_end_${instance.get_instance_data().id}`"
                    :x="render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).x + render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).width" 
                    :y="render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).y"
                    :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                    :width="1"
                    :height="10"
                    @mouseenter="() => on_instance_hover(instance.get_instance_data().id)"
                    @mousedown="() => on_draw_relation(instance.get_instance_data().id)"
                    @mouseleave="on_instance_stop_hover"
                    style="font-size: 10px; cursor: pointer"
                />
                <path 
                    v-for="instance in instance_list.filter(instance => !instance.soft_delete && instance.type === 'relation' && !invisible_labels.includes(instance.label_file_id))"
                    :key="`rel_end_marker_${instance.get_instance_data().id}`"
                    :d="`M ${!insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).x : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).x + render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).width} ${!insatance_orientation_direct(instance) ? render_rects.find(rect => rect.instance_id === instance.get_instance_data().id).y + 10 : render_rects.filter(rect => rect.instance_id === instance.get_instance_data().id).at(-1).y + 10} l -5, -5 l 10, 0 l -5, 5`" 
                    :fill="hover_instance && (hover_instance.get_instance_data().id === instance.get_instance_data().id || hover_instance.from_instance_id === instance.get_instance_data().id || hover_instance.to_instance_id === instance.get_instance_data().id) ? 'red' : instance.label_file.colour.hex"
                />
                <rect 
                    v-for="rect in render_rects"
                    :key="`rect_x_${rect.x}_y_${rect.y}_width_${rect.width}`"
                    :fill="hover_instance && (hover_instance.get_instance_data().id === rect.instance_id || hover_instance.from_instance_id === rect.instance_id || hover_instance.to_instance_id === rect.instance_id) ? 'red' : rect.color"
                    :x="rect.x"
                    :y="rect.y"
                    :width="rect.width"
                    @mouseenter="() => on_instance_hover(rect.instance_id)"
                    @mousedown="() => on_draw_relation(rect.instance_id)"
                    @mouseleave="on_instance_stop_hover"
                    :height="rect.instance_type === 'text_token' ? 3 : 1"
                    style="cursor: pointer"
                />
                <g 
                    v-for="(line, index) in lines"
                    :transform="`translate(0, ${25 + line.y})`"
                    :key="`line_${index}`"
                >
                    <text 
                        v-for="(token, token_index) in tokens.filter(token => token.line === index)"
                        unselectable="on"
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
            </g>
        </svg>
    </div>
</div>
</template>

<script>
import Vue from "vue";
import text_toolbar from "./text_toolbar.vue"
import text_sidebar from "./text_sidebar.vue"
import { CommandManagerAnnotationCore } from "../annotation/annotation_core_command_manager"
import { CreateInstanceCommand } from "../annotation/commands/create_instance_command";
import { UpdateInstanceCommand } from "../annotation/commands/update_instance_command"
import { TextAnnotationInstance, TextRelationInstance } from "../vue_canvas/instances/TextInstance"
import { postInstanceList, getInstanceList } from "../../services/instanceList"
import getTextService from "../../services/getTextService"

export default Vue.extend({
    name: "text_token_core",
    components: {
        text_toolbar,
        text_sidebar
    },
    props: {
        file: {
            type: Object,
            requered: true
        },
        label_list: {
            type: Array,
            requered: true
        }
    },
    data() {
        return {
            text: null,
            current_label: null,
            rendering: true,
            relation_drawing: false,
            initial_words_measures: [],
            lines: [],
            tokens: [],
            instances: [],
            instance_list: [],
            invisible_labels: [],
            //effects
            hover_instance: null,
            //Helpers
            instance_in_progress: null,
            path: {},
            //Render constants
            additional_line_space: 30,
            show_default_navigation: true,
            unselectable: false,
            // Command
            command_manager: undefined,
            has_changed: false,
            save_loading: false,
        }
    },
    mounted() {
        this.hot_key_listeners()
        this.on_mount()
        this.start_autosave()
    },
    computed: {
        render_rects: function() {
            let rects_to_draw = [];
            this.instance_list.filter(instance => !instance.soft_delete && !this.invisible_labels.includes(instance.label_file_id)).map(instance => {
                const instance_rects = this.draw_instance(instance)
                rects_to_draw = [...rects_to_draw, ...instance_rects]
            })
            this.find_intersections(rects_to_draw)
            rects_to_draw = [];
            this.instance_list.filter(instance => !instance.soft_delete  && !this.invisible_labels.includes(instance.label_file_id)).map(instance => {
                const instance_rects = this.draw_instance(instance)
                rects_to_draw = [...rects_to_draw, ...instance_rects]
            })
            this.find_intersections(rects_to_draw)
            return rects_to_draw
        },
        render_drawing_arrow: function() {
            if (!this.instance_in_progress) return {}
            const scroll_y = window.pageYOffset || document.documentElement.scrollTop
            const { x, y } = this.render_rects.find(rect => rect.instance_id === this.instance_in_progress.start_instance)
            return { 
                marker: {
                    x,
                    y
                },
                arrow: {
                    x: this.path.x - 350,
                    y: this.path.y - 100 + scroll_y
                },
                path: `M ${x} ${y} Q ${this.path.x - 350} ${this.path.y - 100 + scroll_y} ${this.path.x - 350} ${this.path.y - 100 + scroll_y}`
             }
        },
        undo_disabled: function() {
            const { command_manager } = this;
            return !command_manager || command_manager.command_history.length == 0 || command_manager.command_index == undefined
        },
        redo_disabled: function() {
            const { command_manager } = this;
            return !command_manager || command_manager.command_history.length == 0 || command_manager.command_index == command_manager.command_history.length - 1
        }
    },
    watch: {
        file: function(newValue) {
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
        hot_key_listeners: function() {
            window.removeEventListener("keydown", this.esk_event_listener)
            window.addEventListener("keydown", this.esk_event_listener)

        },
        esk_event_listener: async function(e) {
            if (e.keyCode === 27) {
                this.instance_in_progress = null
                this.path = {};
                this.unselectable = false
                this.relation_drawing = false;
                window.removeEventListener('mousemove', this.draw_relation_listener)
            }
            else if (e.keyCode === 83) {
                await this.save();
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
            }
        },
        on_draw_text_token: function() {
            if (this.instance_in_progress && this.instance_in_progress.type === "relation") return 
            const selection = window.getSelection()
            const start_token_id = parseInt(selection.anchorNode.parentNode.id)
            const end_token_id = parseInt(selection.focusNode.parentNode.id)
            this.on_start_draw_instance(start_token_id)
            this.on_finish_draw_instance(end_token_id)
            this.instance_in_progress = null
        },
        on_mount: async function() {
            const { nltk: { words } } = await getTextService(this.file.text.tokens_url_signed)
            this.command_manager = new CommandManagerAnnotationCore()
            this.initial_words_measures = words
            setTimeout(() => this.initialize_token_render(), 1000)
            this.initialize_instance_list()
        },
        initialize_token_render: async function() {
            const fixed_svg_width = this.$refs.initial_svg_element.clientWidth;
            const tokens = [];
            let token_x_position = 40;

            this.initial_words_measures.map((word, index) => {
                const current_token_width = this.$refs[`word_${index}`][0].getBoundingClientRect().width

                if (this.lines.length === 0) {
                    this.lines.push({ id: 0, y: 5, initial_y: 5 })
                }
                if (token_x_position + current_token_width > fixed_svg_width) {
                    this.lines.push({id: this.lines.length, y: this.lines[this.lines.length - 1].y + 40, initial_y: this.lines[this.lines.length - 1].y + 40 })
                    token_x_position = 40
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
        },
        change_label_file: function(event) {
            this.current_label = event
        },
        // function to draw relations between instances
        on_draw_relation: async function(instance_id) {
            console.log(instance_id)
            const is_text_token = this.instance_list.find(instance => instance_id === instance.get_instance_data().id).type === "text_token"

            if (!is_text_token) return
            this.unselectable = true

            if (!this.relation_drawing) {
                this.relation_drawing = true
                this.instance_in_progress = {
                    id: this.instances.length,
                    type: "relation",
                    start_instance: instance_id,
                    label_id: this.current_label.id,
                    level: 0
                }
                window.addEventListener('mousemove', this.draw_relation_listener)
                return
            }

            this.unselectable = false

            this.relation_drawing = false;
            this.instance_in_progress.end_instance = instance_id;
            const created_instance = new TextRelationInstance();
            created_instance.create_frontend_instance(
                this.instance_in_progress.start_instance, 
                this.instance_in_progress.end_instance,
                {...this.current_label}
            )
            this.instance_list.push(created_instance)
            const command = new CreateInstanceCommand(created_instance, this)
            this.command_manager.executeCommand(command)
            this.has_changed = true
            this.instance_in_progress = null;
            this.path = {};
            window.removeEventListener('mousemove', this.draw_relation_listener)
        },
        draw_relation_listener: function(e) {
            this.path = {
                x: e.clientX,
                y: e.clientY
            }
        },
        //function to hover on instance
        on_instance_hover: function(instance_id) {
            const instance = this.instance_list.find(instance => instance.get_instance_data().id === instance_id)
            this.hover_instance = instance
        },
        on_instance_stop_hover: function() {
            this.hover_instance = null
        },
        // function to initialize drawing new instance
        on_start_draw_instance: function(start_token) {
            this.instance_in_progress = {
                id: this.instances.length,
                type: "text_token",
                start_token,
                label_id: this.current_label.id,
                level: 0
            }
        },
        // function to finish drawing instance and remove selection
        on_finish_draw_instance: async function(end_token) {
            if (!this.instance_in_progress.start_token) return
            this.instance_in_progress.end_token = end_token
            const instance_exists = this.instances.find(instance => 
                instance.start_token === this.instance_in_progress.start_token && instance.end_token === this.instance_in_progress.end_token
                ||
                instance.end_token === this.instance_in_progress.start_token && instance.start_token === this.instance_in_progress.end_token
                )
            if (!instance_exists) {
                this.instances.push(this.instance_in_progress)
                const created_instance = new TextAnnotationInstance();
                created_instance.create_frontend_instance(
                    this.instance_in_progress.start_token, 
                    this.instance_in_progress.end_token,
                    {...this.current_label}
                )
                this.instance_list.push(created_instance)
                const command = new CreateInstanceCommand(created_instance, this)
                this.command_manager.executeCommand(command)
                this.has_changed = true
            }
            this.instance_in_progress = null
            if (window.getSelection) {
                if (window.getSelection().empty) {  // Chrome
                    window.getSelection().empty();
                } else if (window.getSelection().removeAllRanges) {  // Firefox
                    window.getSelection().removeAllRanges();
                }
                } else if (document.selection) {  // IE?
                document.selection.empty();
            }
        },
        change_instance_label: async function(event) {
            const { instance, label } = event
            const { id, start_token, end_token, label_file, creation_ref_id, from_instance_id, to_instance_id } = instance.get_instance_data()
            if (label.id === label_file.id) return

            let initial_instance;

            if (instance.type === "text_token") {
                initial_instance = new TextAnnotationInstance()
                initial_instance.create_instance(id, start_token, end_token, label_file)
                this.instance_list.map(instance_rel => {
                    if (instance_rel.type === "relation" && (instance_rel.from_instance_id === id || instance_rel.to_instance_id === id)) {
                        instance_rel.soft_delete = true
                        this.command_manager = new CommandManagerAnnotationCore()
                    }
                })
            } else {
                initial_instance = new TextRelationInstance()
                initial_instance.create_instance(id, from_instance_id, to_instance_id, label_file)
            }
            initial_instance.initialized = false
            initial_instance.creation_ref_id = creation_ref_id
            instance.label_file = {...label}
            instance.label_file_id = label.id

            const instance_index = this.instance_list.indexOf(event.instance)
            const command = new UpdateInstanceCommand(instance, instance_index, initial_instance, this)
            this.command_manager.executeCommand(command)
            this.has_changed = true
        },
        delete_instance: async function(instance) {
            const { id, start_token, end_token, label_file, creation_ref_id, from_instance_id, to_instance_id } = instance.get_instance_data()
            let initial_instance;

            if (instance.type === "text_token") {
                initial_instance = new TextAnnotationInstance()
                initial_instance.create_instance(id, start_token, end_token, label_file)
                this.instance_list.map(instance_rel => {
                    if (instance_rel.type === "relation" && (instance_rel.from_instance_id === id || instance_rel.to_instance_id === id)) {
                        instance_rel.soft_delete = true
                        this.command_manager = new CommandManagerAnnotationCore()
                    }
                })
            } else {
                initial_instance = new TextRelationInstance()
                initial_instance.create_instance(id, from_instance_id, to_instance_id, label_file)
            }
            initial_instance.initialized = false
            initial_instance.creation_ref_id = creation_ref_id
            instance.soft_delete = true
            this.hover_instance = null

            const instance_index = this.instance_list.indexOf(instance)
            const command = new UpdateInstanceCommand(instance, instance_index, initial_instance, this)
            this.command_manager.executeCommand(command)
            this.has_changed = true
        },
        change_label_visibility: async function(label) {
            if (label.is_visible) {
                this.invisible_labels = this.invisible_labels.filter(label_id => label_id !== label.id)
            } else {
                this.invisible_labels.push(label.id)
            }
        },
        initialize_instance_list: async function () {
            const { file_serialized: { instance_list } } = await getInstanceList(this.$route.params.project_string_id, this.file.id)
            instance_list.map(instance => {
                if (instance.type === "text_token") {
                    const { id, start_token, end_token, label_file, creation_ref_id } = instance
                    const new_instance = new TextAnnotationInstance()
                    new_instance.create_instance(id, start_token, end_token, label_file)
                    new_instance.creation_ref_id = creation_ref_id
                    this.instance_list.push(new_instance)
                } else {
                    const { id, from_instance_id, to_instance_id, label_file, creation_ref_id } = instance
                    const new_instance = new TextRelationInstance()
                    new_instance.create_instance(id, from_instance_id, to_instance_id, label_file)
                    new_instance.creation_ref_id = creation_ref_id
                    this.instance_list.push(new_instance)
                }
            })
        },
        save: async function (index = null) {
            this.has_changed = false
            this.save_loading = true
            if (!this.instance_in_progress) {
                const res = await postInstanceList(this.$route.params.project_string_id, this.file.id, this.instance_list)
                const {added_instances} = res
                added_instances.map(add_insatnce => {
                    if (!index) {
                        const old_id = this.instance_list.find(instance => instance.creation_ref_id === add_insatnce.creation_ref_id).id
                        this.instance_list.find(instance => instance.creation_ref_id === add_insatnce.creation_ref_id).id = add_insatnce.id
                        if (this.instance_in_progress) {
                            this.instance_in_progress.start_instance = this.instance_in_progress.start_instance === old_id ? add_insatnce.id : this.instance_in_progress.start_instance
                        }
                        this.instance_list
                            .filter(instance => instance.type === "relation" && (instance.from_instance_id === old_id || instance.to_instance_id === old_id))
                            .map(instance => {
                                if (instance.from_instance_id === old_id) instance.from_instance_id = add_insatnce.id
                                else instance.to_instance_id = add_insatnce.id
                            })
                    } else {
                        const old_id = this.instance_list[index].id
                        this.instance_list[index].id = add_insatnce.id
                        this.instance_list
                            .filter(instance => instance.type === "relation" && (instance.from_instance_id === old_id || instance.to_instance_id === old_id))
                            .map(instance => {
                                if (instance.from_instance_id === old_id) instance.from_instance_id = add_insatnce.id
                                else instance.to_instance_id = add_insatnce.id
                            })
                    }
                })
            }
            this.save_loading = false
        },
        undo: function () {
            if (!this.command_manager) {
                return;
            }
            let undone = this.command_manager.undo();
            if (undone) {
                this.has_changed = true;
            }
        },
        redo: function () {
            if (!this.command_manager) {
                return;
            }
            let redone = this.command_manager.redo();
            if (redone) {
                this.has_changed = true;
            }
        },
        change_file(direction, file) {
            if (direction == "next" || direction == "previous") {
                this.$emit("request_file_change", direction, file);
            }
        },
        // Find intersection and update level of the instance
        find_intersections: function(rects_to_draw) {
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
                (entryMap, e) => entryMap.set(e.line, [...entryMap.get(e.line)||[], e]),
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
        update_line_height: function(line_id, level) {
            this.lines.map(line => {
                if (line.id >= line_id) {
                    line.y = line.y + level * this.additional_line_space
                }
            })
        },
        // draw_instance - is only returning rects that have to be drawn
        draw_instance: function(instance) {
            let starting_token;
            let end_token;
            if (instance.type === 'text_token') {
                starting_token = this.tokens.find(token => token.id === instance.start_token)
                end_token = this.tokens.find(token => token.id === instance.end_token)
            } else {
                const start_instance = this.instance_list.find(find_instance =>  find_instance.get_instance_data().id === instance.get_instance_data().from_instance_id)
                starting_token = this.tokens.find(token => token.id === start_instance.start_token)
                const end_instance = this.instance_list.find(find_instance => find_instance.get_instance_data().id === instance.get_instance_data().to_instance_id)
                end_token = this.tokens.find(token => token.id === end_instance.end_token)
            }
            if (starting_token.id === end_token.id) {
                const rect = {
                    instance_id: instance.get_instance_data().id,
                    x: starting_token.start_x,
                    y: this.lines[starting_token.line].y + 3,
                    line: starting_token.line,
                    width: starting_token.width,
                    instance_type: instance.type,
                    color: instance.label_file.colour.hex
                }
                return [rect]
            }
            
            if (starting_token.line === end_token.line) {
                if (starting_token.id < end_token.id) {
                    const rect = {
                        instance_id: instance.get_instance_data().id,
                        x: starting_token.start_x,
                        y: this.lines[starting_token.line].y + 3,
                        line: starting_token.line,
                        width: end_token.start_x + end_token.width - starting_token.start_x,
                        instance_type: instance.type,
                        color: instance.label_file.colour.hex
                    }
    
                    return [rect]
                } else {
                    const rect = {
                        instance_id: instance.get_instance_data().id,
                        x: end_token.start_x,
                        y: this.lines[end_token.line].y + 3,
                        line: starting_token.line,
                        width: starting_token.start_x + starting_token.width - end_token.start_x,
                        instance_type: instance.type,
                        color: instance.label_file.colour.hex
                    }
    
                    return [rect]
                }
            }

            if (starting_token.line !== end_token.line) {
                if (starting_token.id > end_token.id) {
                    const rects = [];
                    for (let i = end_token.line; i <= starting_token.line; ++i) {
                        if (i === starting_token.line) {
                            const first_token_in_the_line = this.tokens.find(token => token.line == starting_token.line)
                            const rect = {
                                instance_id: instance.get_instance_data().id,
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: starting_token.start_x + starting_token.width - first_token_in_the_line.start_x,
                                instance_type: instance.type,
                                color: instance.label_file.colour.hex
                            }
                            rects.push(rect)
                        }
                        else if (i === end_token.line) {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == end_token.line)
                            const rect = {
                                instance_id: instance.get_instance_data().id,
                                x: end_token.start_x,
                                y: this.lines[end_token.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - end_token.start_x,
                                instance_type: instance.type,
                                color: instance.label_file.colour.hex
                            }
                            rects.push(rect)
                        }
                        else {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == this.lines[i].id)
                            const first_token_in_the_line = this.tokens.find(token => token.line == this.lines[i].id)
                            const rect = {
                                instance_id: instance.get_instance_data().id,
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - first_token_in_the_line.start_x,
                                instance_type: instance.type,
                                color: instance.label_file.colour.hex
                            }
                            rects.push(rect)
                        }
                    }
                    return rects
                } else {
                    const rects = [];
                    for (let i = starting_token.line; i <= end_token.line; ++i) {
                        if (i === starting_token.line) {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == starting_token.line)
                            const rect = {
                                instance_id: instance.get_instance_data().id,
                                x: starting_token.start_x,
                                y: this.lines[starting_token.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - starting_token.start_x,
                                instance_type: instance.type,
                                color: instance.label_file.colour.hex
                            }
                            rects.push(rect)
                        }
                        else if (i === end_token.line) {
                            const first_token_in_the_line = this.tokens.find(token => token.line == end_token.line)
                            const rect = {
                                instance_id: instance.get_instance_data().id,
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: end_token.start_x + end_token.width - first_token_in_the_line.start_x,
                                instance_type: instance.type,
                                color: instance.label_file.colour.hex
                            }
                            rects.push(rect)
                        }
                        else {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == this.lines[i].id)
                            const first_token_in_the_line = this.tokens.find(token => token.line == this.lines[i].id)
                            const rect = {
                                instance_id: instance.get_instance_data().id,
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - first_token_in_the_line.start_x,
                                instance_type: instance.type,
                                color: instance.label_file.colour.hex
                            }
                            rects.push(rect)
                        }
                    }
                    return rects
                }
            }
            const trial_rect = {
                x: starting_token.start_x,
                y: this.lines[starting_token.line].y + 3,
                width: starting_token.width,
                instance_type: instance.type
            }
            return [trial_rect]
        },
        // this is function to check what direction relation arrow should piint to
        insatance_orientation_direct: function(relational_instance) {
            const start_instance = this.instance_list.find(find_instance => find_instance.get_instance_data().id === relational_instance.get_instance_data().from_instance_id)
            const starting_token = this.tokens.find(token => token.id === start_instance.start_token)
            const end_instance = this.instance_list.find(find_instance => find_instance.get_instance_data().id === relational_instance.get_instance_data().to_instance_id)
            const end_token = this.tokens.find(token => token.id === end_instance.end_token)
            return starting_token.id < end_token.id
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