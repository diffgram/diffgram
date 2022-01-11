<template>
    <v-toolbar 
        v-if="show_toolbar"
        dense
        width="100%"
        elevation="0"
        fixed
        :height="50"
        style="overflow: hidden; padding:0; border-bottom: 1px solid #e0e0e0"
    >
        <v-toolbar-items class="pl-0 ml-0" style="border: 1px solid #e0e0e0;">
            <div style="width: 310px">
                <div class="pl-2 pr-3 pt-4">
                    <label_select_annotation
                        :project_string_id="project_string_id"
                        :label_file_list="label_list"
                        :label_file_colour_map="label_file_colour_map"
                        @change="$emit('change_label', $event)"
                        :loading="loading"
                        :request_refresh_from_project="true"
                        :show_visibility_toggle="true"
                    />
                </div>
            </div>
            <v-divider vertical />
            <div style="display: flex; align-items: center; justify-content: center; height: 100%">
                <v-switch
                    v-model="sentance_mode"
                    label="Sentense mode"
                    @change="$emit('change_text_mode')"
                />
            </div>
        </v-toolbar-items>
    </v-toolbar>
</template>

<script>

  import Vue from "vue";
  import label_select_annotation from "../label/label_select_annotation.vue";

  export default Vue.extend({
      name: 'text_toolbar',
      components: {
          label_select_annotation
      },
      props: {
          label_list: {
              type: Array,
              default:[]
          },
          sentance_mode: {
              type: Boolean,
              required: true
          }
      },
      data() {
          return {
              show_toolbar: true
          }
      }
  })

</script>