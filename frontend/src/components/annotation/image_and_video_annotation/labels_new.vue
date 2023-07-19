<template>
  <div v-cloak>

    <v-layout>
      <v-flex>
        <v-text-field
            required
            :counter="30"
            data-cy="label_name_text_field"
            label="Label Name"
            v-model="new_label_name"
            :disabled="loading"
            class="pl-2 pr-2"
            >
        </v-text-field>

        <v-container>
          <slider-picker data-cy="color-slider"
                         v-model="colour" />
        </v-container>

      </v-flex>
    </v-layout>

    <v-card-actions class="pa-2">

      <standard_button
          button_message="Create"
          button_color="primary"
          datacy="create_label_button"
          @click="new_label_function"
          :loading="loading"
          :disabled="!new_label_name || loading"
          icon="mdi-check"
          tooltip_message="(Enter)"
          :bottom="true"
          :left="true"
          xLarge>
      </standard_button>

      <v-spacer> </v-spacer>

      <standard_button
        tooltip_message="Info"
        href="https://diffgram.readme.io/docs/create-your-first-label"
        target="_blank"
        icon="info"
        :icon_style="true"
        color="secondary">
    </standard_button>

    </v-card-actions>

    <v_error_multiple :error="error">
    </v_error_multiple>



  </div>
</template>

<script lang="ts">

import axios from '../../../services/customInstance';

import Vue from "vue"; export default Vue.extend( {
  name: 'labels_new',

  props: {
    menu_open: {
      default: false
    },
    schema_id: {
      required: true
    }
  },

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

      error: {},

      current_label: {
        id: null
      },

      Labels: []
    }
  },
  mounted: function () {
    window.addEventListener('keydown', this.hotkeys);
  },
  beforeDestroy() {
    window.removeEventListener('keydown', this.hotkeys);
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
          schema_id: this.schema_id

      }).then(response => {

        this.new_label_name = null
        this.loading = false

        // only if success?
        this.$store.commit('init_label_refresh')
        this.$emit('label_created', response.data.label)
        }).catch(error => {
          this.loading = false

          if (error)  {
              this.error = this.$route_api_errors(error)
          }
      });

    },

    hotkeys: function (event) {
      if (this.$props.menu_open == false){
        return
      }
      if (event.key === 'Enter') {
        this.new_label_function()
      }
    },
  }
}

) </script>
