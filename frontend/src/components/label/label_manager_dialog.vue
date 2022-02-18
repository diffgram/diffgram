<template>
  <div v-cloak>

    <v-dialog v-model="is_open" max-width="1000px" id="export-dialog">
       <v-card elevation="0">
         <labels_view @label_created="on_label_created"
                      :show_attributes_table="true"
                      :show_edit_templates="true"
                      :project_string_id="project_string_id"
                      class="pa-8"></labels_view>
       </v-card>
    </v-dialog>

  </div>
</template>

<script lang="ts">
  import labels_view from '../../components/annotation/labels_view'
  import Vue from "vue";

  export default Vue.extend({

      name: 'label_manager_dialog',
      components: {
        labels_view: labels_view
      },
      props: ['project_string_id'],

      watch: {},
      mounted() {

      },

      data() {
        return {
          is_open: false
        }
      },

      methods: {
        on_label_created: function(label){
          this.$emit('label_created', label)
        },
        open() {
          this.is_open = true;
        }
      }
    }
  ) </script>
