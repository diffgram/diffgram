<template>
    <v-toolbar
        dense
        width="100%"
        elevation="0"
        fixed
        :height="height"
        style="overflow: hidden; padding: 0; border-bottom: 1px solid #e0e0e0"
    >
        <v-toolbar-items>
            <div style="width: 10px" />
            <tooltip_button
                color="primary"
                icon="mdi-undo"
                tooltip_message="Undo (ctrl+z)"
                ui_schema_name="undo"
                :disabled="undo_disabled"
                :icon_style="true"
                :bottom="true"
                @click="$emit('undo')"
            />

            <tooltip_button
                color="primary"
                icon="mdi-redo"
                tooltip_message="Redo (ctrl+y)"
                ui_schema_name="redo"
                :disabled="redo_disabled"
                :icon_style="true"
                :bottom="true"
                @click="$emit('redo')"
            />

            <v-divider vertical></v-divider>

            <div style="width: 310px">
                <div class="pl-2 pr-3 pt-4">
                    <label_select_annotation
                        :project_string_id="project_string_id"
                        :label_file_list="label_list"
                        :label_file_colour_map="label_file_colour_map"
                        :loading="loading"
                        :request_refresh_from_project="true"
                        :show_visibility_toggle="true"
                        @change="$emit('change_label_file', $event)"
                        @update_label_file_visible="$emit('update_label_file_visibility', $event)"
                    />
                </div>
            </div>

            <v-divider vertical></v-divider>

            <div>
                <tooltip_button
                    ui_schema_name="save"
                    @click="$emit('save')"
                    datacy="save_button"
                    :loading="save_loading"
                    :disabled="
                        !has_changed ||
                        save_loading ||
                        view_only_mode ||
                        (file == undefined && task == undefined)
                    "
                    color="primary"
                    icon="save"
                    tooltip_message="Save Image / Frame"
                    :icon_style="true"
                    :bottom="true"
                    >
                </tooltip_button>
            </div>
            <div class="has-changed">
                <div style="width: 100px">
                <span v-if="save_loading"> Saving. </span>
                <span v-else>
                    <span v-if="has_changed">Changes Detected...</span>
                    <span v-else>Saved</span>
                </span>
                </div>
            </div>

            <v-divider vertical></v-divider>

            <div>
                <tooltip_button
                tooltip_message="Previous File"
                @click="$emit('change_file', 'previous')"
                :disabled="
                    loading || annotations_loading || full_file_loading || !file
                "
                color="primary"
                icon="mdi-chevron-left-circle"
                :icon_style="true"
                :bottom="true"
                >
                </tooltip_button>
                <!-- TODO Move some of disabled logic into functions don't like having
                    so much of it here as it gets more complext -->
            </div>
            <div>
                <tooltip_button
                tooltip_message="Next File"
                @click="$emit('change_file', 'next')"
                :disabled="
                    loading || annotations_loading || full_file_loading || !file
                "
                color="primary"
                icon="mdi-chevron-right-circle"
                :icon_style="true"
                :bottom="true"
                >
                </tooltip_button>
            </div>

            <v-divider vertical></v-divider>

            <button_with_menu
                tooltip_message="Hotkeys"
                color="primary"
                icon="mdi-keyboard-settings"
                :close_by_button="true"
            >
            </button_with_menu>

            <v-divider vertical></v-divider>

        </v-toolbar-items>
    </v-toolbar>
</template>

<script>
import Vue from 'vue'
import label_select_annotation from "../label/label_select_annotation.vue"

export default Vue.extend({
    name: "text_toolbar",
    components: {
        label_select_annotation
    },
    props: {
        undo_disabled: {
            type: Boolean,
            required: true
        },
        redo_disabled: {
            type: Boolean,
            required: true
        },
        has_changed: {
            type: Boolean,
            default: false
        },
        save_loading: {
            type: Boolean,
            default: false
        }
    }
})
</script>