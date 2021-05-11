<template>
  <div v-cloak >
    <v-layout >


      <v-select :items="label_list_with_limit"
                v-model="selected"
                :label="label_prompt"
                return-object
                :data-cy="datacy"
                :disabled="label_refresh_loading || view_only_mode"
                @change="emit_selected()"
                item-value="id"
                >

        <template v-slot:item="data">

          <v-icon left
                  :style="style_color(data.item.colour.hex)">
            flag
          </v-icon>

          <tooltip_icon
            v-if="data.item.label.default_sequences_to_single_frame"
            tooltip_message="Video Defaults to Single Frame"
            icon="mdi-flag-checkered"
            color="black">
          </tooltip_icon>

          <v-chip color="white"
                  text-color="primary">
            {{data.item.label.name}}
          </v-chip>


          <div v-if="show_visibility_toggle
                  || data.item.is_visible == false">

            <v-layout>

              <div v-if="data.item.is_visible == true
                    || data.item.is_visible == null">
                <v-btn icon @click="toggle_label_visible(data.item)">
                  <v-icon color="blue">remove_red_eye</v-icon>
                </v-btn>
              </div>

              <div v-if="data.item.is_visible == false">
                <v-btn icon @click="toggle_label_visible(data.item)">
                  <v-icon color="grey">remove_red_eye</v-icon>
                </v-btn>
              </div>

            </v-layout>
            </div>


          <!--
          <div v-if="$store.state.user.current.is_super_admin === true">
            {{ data.item.id }}
          </div>
          -->

        </template>

        <template v-slot:selection="data">

          <v-chip color="white">
            <v-icon
              :style="style_color(data.item.colour.hex)">
              flag
            </v-icon>

            <v-icon v-if="data.item.label.default_sequences_to_single_frame"
                    color="black">
              mdi-flag-checkered
            </v-icon>

            {{ data.item.label.name}}
          </v-chip>

        </template>


      </v-select>

    </v-layout>

  </div>
</template>

<!--

-->

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue";

  export default Vue.extend({

      name: 'label_select_annotation',

      props: {
        'project_string_id': {},
        'view_only_mode': {},
        'datacy': {
          default: 'label_select_annotation',
          type: String
        },
        'label_file_list': {},
        'label_file_colour_map': {},
        'request_refresh_from_project': {
          default: null
        },
        'video_mode': {
            default: false,
            type: Boolean
        },
        'loading': {},
        'label_prompt': {
          default: 'Label'
        },
        'show_visibility_toggle': {
          default: false
        },
        'select_this_id_at_load': {},
      },

      watch: {

        request_refresh_from_project: function () {
          this.refresh_label_list_from_project()
        },

      },
      mounted() {

        if (this.label_file_list_prop) {
          this.label_list = this.label_file_list_prop
          this.selected = this.label_file_list_prop[0]
        } else {
          this.refresh_label_list_from_project()
        }

        if (this.select_this_id_at_load) {
          this.selected = this.label_list.find(obj => {
            return obj.id == this.select_this_id_at_load
          })
          this.emit_selected() // in case something relies on this,
          // ie the data circles back / watching $event
          // TODO consider v-model for selected in this context.
        }

      },

      computed: {

        label_list_with_limit: function () {
          if (!this.$props.limit) {
            this.over_limit = false
            return this.label_list
          }
          if (this.label_list.length > this.$props.limit) {
            this.over_limit = true
          }
          return this.label_list.slice(0, this.$props.limit)
        },

      },
      data() {
        return {

          label_refresh_loading: false,

          selected: {},

          label_list: [],

        }
      },

      methods: {

        toggle_label_visible(label) {
          if (typeof label.is_visible == "undefined") {
            label.is_visible = false
          } else {
            label.is_visible = !label.is_visible
          }
          this.label_list.splice(this.label_list.indexOf(label), 1, label)
          this.$emit('update_label_file_visible', label)
        },


        refresh_label_list_from_project: function () {

          var url = null
          this.label_refresh_loading = true

          url = '/api/project/' + this.$store.state.project.current.project_string_id
            + '/labels/refresh'

          axios.get(url, {})
            .then(response => {

              this.label_list = response.data.labels_out
              this.emit_selected()
              this.label_refresh_loading = false

            })
            .catch(error => {
              console.log(error);
            });

        },

        style_color: function (hex) {
          return "color:" + hex
        },

        emit_selected: function () {
          this.$emit('change', this.selected)
        }

      }
    }
  ) </script>
