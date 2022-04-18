<template>
    <div>
        <main_menu
            :height="`${!task ? '100px' : '50px'}`"
            :show_default_navigation="!task"
        >
            <template slot="second_row">
                <geo_toolbar 
                    :instance_type_list="instance_type_list" 
                    :draw_mode="draw_mode"
                    :undo_disabled="undo_disabled"
                    :redo_disabled="redo_disabled"
                    :has_changed="has_changed"
                    :project_string_id="project_string_id"
                    :label_list="label_list"
                    :label_file_colour_map="label_file_colour_map"
                    :task="task"
                    :file="file"
                    @edit_mode_toggle="change_mode" 
                    @change_instance_type="change_instance_type"
                    @change_label_file="change_label_file"
                    @change_label_visibility="change_label_visibility"
                    @change_file="change_file"
                    @undo="undo()"
                    @redo="redo()"
                />
            </template>
        </main_menu>
        <div style="display: flex; flex-direction: row">
            <geo_sidebar
                :instance_list="instance_list ? instance_list.get() : []"
                :label_list="label_list"
                :label_file_colour_map="label_file_colour_map"
                @delete_instance="delete_instance"
                @change_instance_label="change_instance_label"
            />
            <div 
                id="map" 
                ref="map" 
                @click="draw_instance" 
                :style="`height: calc(100vh - 100px); z-index: 0; width: 100%; cursor: ${cursor}`"
            />
        </div>
    </div>
</template>

<script>
import Vue from "vue";
import geo_toolbar from "./geo_toolbar.vue"
import geo_sidebar from "./geo_sidebar.vue"
import CommandManager from "../../helpers/command/command_manager"
import InstanceList from "../../helpers/instance_list"
import History from "../../helpers/history"

export default Vue.extend({
    name: "text_token_core",
    data() {
        return {
            instance_list: undefined,
            history: undefined,
            command_manager: undefined
        }
    },
    components: {
        geo_toolbar,
        geo_sidebar
    },
    computed: {},
    watch: {},
    mounted() {
        this.instance_list = new InstanceList()
        this.history = new History()
        this.command_manager = new CommandManager(this.history)
    },
    methods: {
        initialize_interface: function() {
            // Get instances from teh backend and render them
        },
        draw_instance: function() {
            //Start drawing instance depending on the current instance type
        },
        change_mode: function() {
            // Change between draw and annotate modes
        },
        delete_instance: function() {
            // Delete instance and remove from teh map
        },
        change_instance_label: function() {
            // change label of the instance
        },
        change_label_visibility: function() {
            // Changing visibility of the label
        },
        change_instance_type: function() {
            // Change current instance type
        },
        change_label_file: function() {
            //Chaging current label
        },
        undo: function() {
            // Undo function
        },
        redo: function() {
            // Redo fucntion
        },
        save: function() {
            // Save
        },
        on_mount_hotkeys: function() {
            // Setting howtkeys for the geo interface
        }
    }
})
</script>

