<template>
  <div v-cloak>

    <v-layout>
      <v-flex>

        <v-card-title>
          New
        </v-card-title>

        <v-text-field required
                      :counter="30"
                      data-cy="label_name_text_field"
                      label="Name"
                      v-model="new_label_name"
                      :rules="[rules.new_label_name]"
                      :disabled="loading">
        </v-text-field>

        <v-container>
          <!-- Maybe hide on mobile? or something... -->
          <slider-picker data-cy="color-slider" v-model="colour" />
        </v-container>


        <!-- Advanced stuff-->
        <v-container>

          <v-expansion-panels>
            <v-expansion-panel>

              <v-expansion-panel-header>
                  Advanced Info
              </v-expansion-panel-header>

              <v-expansion-panel-content>
                <v-card>

                    <v-alert type="info"

                                dismissible>

                      <ul>
                        <li> Labels are created in the context of the project.
                          <br> For example, Labels created in the Studio are accessible to the whole project. </li>
                        <li> Existing tasks are unaffected by new label creation. </li>
                      </ul>

                        <v-btn
                              href="https://diffgram.readme.io/docs/create-your-first-label"
                              target="_blank"
                              >
                          <v-icon left>mdi-book</v-icon>
                          More on Labels
                          <v-icon right>mdi-open-in-new</v-icon>
                        </v-btn>
                      </v-alert>

                </v-card>

            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>


          <v-expansion-panels>
            <v-expansion-panel>

              <v-expansion-panel-header>
                Advanced Options
              </v-expansion-panel-header>

              <v-expansion-panel-content>
                  <v-card>
                    <v-container>
                      <h3> Sequence Special Option </h3>
                      <v-checkbox label="New Sequences Default to Single Frame"
                                  data-cy="default_sequences_to_single_frame"
                                  v-model="default_sequences_to_single_frame"
                                  >

                      </v-checkbox>
                    </v-container>
                  </v-card>

            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>

        </v-container>

      </v-flex>
      <v-flex xs12 sm6>

      </v-flex>
    </v-layout>

    <v-card-actions class="pa-2">

      <v-btn color="primary"
             data-cy="create_label_button"
              @click="new_label_function"
              :loading="loading"
              :disabled="loading"
              large
              >
        Create
      </v-btn>

    </v-card-actions>

    <v_error_multiple :error="error">
    </v_error_multiple>


  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'labels_new',
  props: [
  ],
  data() {
    return {

      colour: {
        hex: '#194d33',
        hsl: { h: 150, s: 0.5, l: 0.2, a: 1 },
        hsv: { h: 150, s: 0.66, v: 0.30, a: 1 },
        rgba: { r: 25, g: 77, b: 51, a: 1 },
        a: 1
      },

      loading: false,

      new_label_name: null,

      default_sequences_to_single_frame: false,

      error: {},

      current_label: {
        id: null
      },

      Labels: [],

      rules: {
        required: (value) => !!value || 'Required.',
        new_label_name: (value) => {
          const pattern = new RegExp("^[a-zA-Z0-9_ ]{1,30}$")
          return pattern.test(value) || 'No special characters. Between 1 - 30 characters.'
        }
      }
    }
  },
  computed: {
  },
  created() {

  },
  methods: {

    new_label_function: function () {

      this.loading = true
      this.error = {}

      axios.post('/api/v1/project/' +
        String(this.$store.state.project.current.project_string_id) +
        '/label/new', {

          colour: this.colour,
          name: this.new_label_name,
          default_sequences_to_single_frame: this.default_sequences_to_single_frame


      }).then(response => {

        this.new_label_name = null
        this.loading = false

        // only if success?
        this.$store.commit('init_label_refresh')
        this.$emit('label_created', response.data.label)
        }).catch(error => {
          this.loading = false

          if (error)  {
              if (error.response.status == 400) {
                this.error = error.response.data.log.error
              }
          }

      });

    }

  }
}

) </script>
