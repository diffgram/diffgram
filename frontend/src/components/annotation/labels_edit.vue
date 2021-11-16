<template>
  <div v-cloak>

    <!-- TODO merge this component
          with label_new. Shared UI
          stuff is key to reuse here-->


    <v-layout >
      <v-flex>

        <v-card-title>
          Edit

          <v-spacer>
          </v-spacer>


        </v-card-title>

        <v-text-field required
                      :counter="30"
                      label="Name"
                      v-if="current_label_file.label"
                      v-model="current_label_file.label.name"
                      :rules="[rules.new_label_name]"
                      :disabled="loading">
        </v-text-field>
        {{ new_label_error }}

        <v-container v-if="current_label_file.colour != undefined">
          <slider-picker v-model="current_label_file.colour" />
        </v-container>

      </v-flex>

        <v-container>

          <v-expansion-panels>
            <v-expansion-panel>
              <div slot="header">Advanced Edit Info</div>

              <v-expansion-panel-content>
                <v-card>
                  <v-container>

                <v-alert type="info"
                            dismissible>

                  <ul>
                    <li> Labels edited reflect on the Project and <b>new</b> Tasks. </li>
                    <li> Existing tasks are not directly affected by label edits. </li>
                  </ul>

                    <v-btn color="white darken-2"
                          href="https://diffgram.readme.io/docs/timing-of-work"
                          target="_blank"
                          >
                      <v-icon left>mdi-book</v-icon>
                      Timing of Work
                      <v-icon right>mdi-open-in-new</v-icon>
                    </v-btn>
                  </v-alert>

                  </v-container>
                </v-card>

            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>

          <v-expansion-panels>
            <v-expansion-panel>
              <v-expansion-panel-content>
              <div slot="header">Advanced Options</div>

              <v-card>
                <v-container>
                  <h3> Video Defaults </h3>
                  <v-checkbox
                    label="New Sequences Default to Single Frame"
                    v-model="current_label_file.label.default_sequences_to_single_frame"
                    >

                  </v-checkbox>
                </v-container>
              </v-card>

            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>

        </v-container>

    </v-layout>

    <v-card-actions>

      <v-btn color="primary"
              @click="edit"
              :loading="loading"
              @click.native="loader = 'loading'"
              :disabled="loading">
        Update
      </v-btn>


    </v-card-actions>




  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'label_edit',
  props: [
    'label_file_prop',
    'edit_label_menu',
    'project_string_id'
  ],
  data() {
    return {

      loading: false,

      // Caution
      // we load existing file
      // from label_file_prop, see mounted()
      current_label_file: {
        name: null,
        colour: {
          hex: '#194d33',
          hsl: { h: 150, s: 0.5, l: 0.2, a: 1 },
          hsv: { h: 150, s: 0.66, v: 0.30, a: 1 },
          rgba: { r: 25, g: 77, b: 51, a: 1 },
          a: 1
        },
        label: {}
      },
      error_name: null,

      new_label_error: null,


      rules: {
        required: (value) => !!value || 'Required.',
        new_label_name: (value) => {
          const pattern = new RegExp("^[a-zA-Z0-9_ ]{1,30}$")
          return pattern.test(value) || 'No special characters. Between 1 - 30 characters.'
        }
      }
    }
  },
  mounted() {

    // Label()
    this.current_label_file = {...this.label_file_prop}
    this.current_label_file.label = {...this.label_file_prop.label}
  },
  methods: {


    async edit() {
      this.loading = true;
      try{
        const response = await axios.post(`/api/project/${String(this.$store.state.project.current.project_string_id)}/labels/edit`,
          {
            label_file: this.current_label_file
          })
        this.$store.commit('init_label_refresh')
        this.$emit('request_boxes_refresh')
        this.$emit('label_updated', {...this.current_label_file})
      }
      catch (error) {
        console.error(error);
      }
      finally {
        this.loading = false;
      }



    },
    cancel() {
      this.$store.commit('init_label_refresh')
    },
    remove: function () {

      axios.post('/api/project/' +
        this.project_string_id + '/file/remove', {
          file: this.current_label_file
        })
        .then(response => {
          if (response.data.success === true) {
            //this.$emit('remove_file_request', file)
          }
        })
        .catch(error => {
          console.error(error);
        });

    }

  }
}

) </script>
