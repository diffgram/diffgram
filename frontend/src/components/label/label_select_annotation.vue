<template>
  <div v-cloak  id="label_select_annotation">
    <v-layout >


      <v-select :items="label_list_with_limit"
                v-model="selected"
                :label="label_prompt"
                return-object
                :data-cy="datacy"
                :disabled="label_refresh_loading"
                @change="emit_selected()"
                item-value="id"
                data-cy="label_select"
                ref="label_select"
                class="ma-0"
                >

        <template v-slot:item="data">

          <v-icon left
                  :style="style_color(data.item.colour.hex)">
            flag
          </v-icon>

          <div class="pl-4 pr-4"
               :data-cy="data.item.label.name">
            {{data.item.label.name}}
           </div>

          <!-- Would like to have this but it looks kind of messy -->
          <!--
          <div style="color: grey">
            {{label_list.indexOf(data.item) + 1}}</div>
          -->

          <tooltip_icon
            v-if="data.item.label.default_sequences_to_single_frame"
            tooltip_message="Video Defaults to Single Frame"
            icon="mdi-flag-checkered"
            color="black">
          </tooltip_icon>


          <div v-if="show_visibility_toggle
                  || data.item.is_visible == false">

            <v-layout>

              <div v-if="data.item.is_visible == true
                    || data.item.is_visible == null">
                <tooltip_button
                  @click="toggle_label_visible(data.item)"
                  color="grey lighten-1"
                  :icon_style="true"
                  icon="remove_red_eye"
                  tooltip_message="Hide"
                  :bottom="true">
                </tooltip_button>
              </div>

              <div v-if="data.item.is_visible == false">
                <tooltip_button
                  @click="toggle_label_visible(data.item)"
                  color="grey"
                  :icon_style="true"
                  icon="mdi-eye-off"
                  tooltip_message="Show"
                  :bottom="true">
                </tooltip_button>
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

          <div>
            <v-icon
              left
              :style="style_color(data.item.colour.hex)">
              flag
            </v-icon>

            <v-icon v-if="data.item.label.default_sequences_to_single_frame"
                    color="black">
              mdi-flag-checkered
            </v-icon>

            {{ label_name_truncated(data.item.label.name) }}
          </div>

        </template>

        <template v-slot:no-data>
          No Labels Templates Created.
          <v-btn color="primary" small @click="$router.push(`/project/${computed_project_string_id}/labels`)">Create Label Templates</v-btn>
        </template>
      </v-select>

    </v-layout>

  </div>
</template>

<!--

-->

<script lang="ts">

  import axios from '../../services/customAxiosInstance';

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
        'default_hot_keys': {
          default: 'w'
        },
        'label_file_colour_map': {},
        'request_refresh_from_project': {
          default: null
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

        window.addEventListener('keyup', this.keyboard_events_window);

      },

      beforeDestroy() {
        window.removeEventListener('keyup', this.keyboard_events_window)
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
        computed_project_string_id: function () {
          if (this.$props.project_string_id) {
            return this.$props.project_string_id;
          }
          return this.$store.state.project.current.project_string_id;
        },


      },
      data() {
        return {

          label_refresh_loading: false,

          selected: {},

          label_list: [],

          hotkey_dict: {
            49: 0,
            50: 1,
            51: 2,
            52: 3,
            53: 4,
            54: 5,
            55: 6,
            56: 7,
            57: 8,
            58: 9
          },

        }
      },

      methods: {

        label_name_truncated: function(name) {
          let max_size = 23
          let default_selector_size = 290 // feels pretty brittle
          if (document.getElementById('label_select_annotation').offsetWidth
                < default_selector_size) {
            max_size = 5
          }
          if (name.length > max_size) {
            return name.slice(0, max_size) + '...'
          } else {
            return name
          }
        },

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
          url = '/api/project/' + this.computed_project_string_id
            + '/labels/refresh'

          axios.get(url, {})
            .then(response => {

              this.label_list = response.data.labels_out
              this.selected = this.label_list[0]
              this.emit_selected()
              this.label_refresh_loading = false

            })
            .catch(error => {
              console.error(error);
            });

        },

        toggle_label_menu: function () {
          this.$refs['label_select'].isMenuActive = !this.$refs['label_select'].isMenuActive;
        },

        style_color: function (hex) {
          return "color:" + hex
        },

        emit_selected: function () {
          this.$emit('change', this.selected)
        },

        keyboard_events_window: function (event) {

          if (this.$store.state.user.is_typing_or_menu_open == true) {
            return
          }
          if (event.key === this.$props.default_hot_keys) {
            this.toggle_label_menu()
            return
          }

          let hotkey = null
          hotkey = this.hotkey_dict[event.keyCode]
          if (hotkey != null) {
            this.selected = this.label_list[hotkey]
            this.emit_selected()
          }

        },

      }
    }
  ) </script>
