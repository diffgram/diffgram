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
                    @change="$emit('change_label_file', $event)"
                    :loading="loading"
                    :request_refresh_from_project="true"
                    :show_visibility_toggle="true"
                    @update_label_file_visible="
                        $emit('update_label_file_visibility', $event)
                    "
                    />
                </div>
            </div>

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
        }
    }
})
</script>