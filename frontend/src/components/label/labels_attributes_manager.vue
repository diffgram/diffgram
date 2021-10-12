<template>
  <v-layour class="pa-0">
    <v-layout>
      <v-row>
        <v-col cols="6">
          <div class="d-flex align-center justify-space-between">
            <h1 class="font-weight-medium text--primary">Labels:</h1>
            <button_with_menu
              datacy="new_label_template"
              button_text="Create Label"
              tooltip_message="Create Label"
              small
              @click="$store.commit('set_user_is_typing_or_menu_open', true)"
              @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
              icon="add"
              icon_color="white"
              color="primary"
              offset="x"
            >

              <template slot="content">

                <v_labels_new @label_created="on_label_created">
                </v_labels_new>

              </template>

            </button_with_menu>
          </div>
          <v-list v-if="label_file_list.length > 0">
            <v-list-item v-for="label_file in label_file_list">
              <v-icon>mdi-flag</v-icon>
              {{label_file.label.name}}
            </v-list-item>
          </v-list>
          <v-container v-else style="min-height: 500px" class="d-flex flex-column justify-center align-center">
            <h1 class="font-weight-medium text--primary text-center">No Labels Yet</h1>
            <v-icon color="secondary" size="128">mdi-flag</v-icon>
            <h4 class="font-weight-medium text--primary text-center">
              Create one by clicking the "Create Label Button"
            </h4>
          </v-container>
        </v-col>
        <v-col cols="6" v-if="selected_label">
          <h1  class="font-weight-medium text--primary">Attributes for: {name goes here}</h1>
        </v-col>
      </v-row>
    </v-layout>
  </v-layour>

</template>

<script lang="ts">

  import axios from 'axios';
  import Vue from "vue";

  export default Vue.extend({
      name: 'labels_attributes_manager',

      props: {
        'project_string_id': {},
      },
      watch: {},
      async mounted() {
        await this.fetch_labels();

      },
      data() {
        return {
          labels_loading: false,
          selected_label: null,
          label_file_list: [],
          label_file_colour_map: {}
        }
      },

      methods: {
        on_label_created: function(label_file){
          this.label_file_list.push(label_file)
        },
        fetch_labels: async function(){

          if (this.$props.project_string_id == null) {
            return
          }

          try{
            var url = `/api/project/${this.project_string_id}/labels/refresh`
            this.labels_loading = true

            const response = await axios.get(url, {})
            this.label_file_list = response.data.labels_out

            this.label_file_colour_map = response.data.label_file_colour_map

            this.label_refresh_loading = false
            this.$emit('labels_fetched', this.label_file_list)


          }
          catch (e) {
            console.error(e)
          }
        }
      }
    }
  ) </script>
