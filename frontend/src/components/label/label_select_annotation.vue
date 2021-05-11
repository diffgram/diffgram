<template>
  <div v-cloak >
    <v-layout >

      <!--
        Goal: User selectable, assumes only one selected at a time.
      -->


      <v-select :items="label_list_with_limit"
                v-model="selected"
                :label="label_prompt"
                return-object
                :data-cy="datacy"
                :multiple="multiple"
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

  Example usage

              <label_select_only
             :project_string_id="project_string_id"
              @label_file="recieve_label_file($event)"
                               >
            </label_select_only>

  NOT GLOBALLY available as of Jan 29 2020
  so import ie:
  import label_select_only from '../label/label_select_only.vue'
    components: {
    label_select_only
  },

  TODO look at using v-model so don't have to use @label_file


  CAUTION be aware when editing
    this can be used in a "view_only_mode" so check not equal for that context

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
      },

      watch: {

        request_refresh_from_project: function () {
          this.refresh_label_list_from_project()
        },

        load_selected_id_list: function () {
          this.refresh_internal_selected()
        }

      },
      mounted() {

        if (this.label_file_list_prop) {
          // Note we are setting selected here
          this.selected = this.label_file_list_prop
          this.label_list = this.label_file_list_prop
          this.check_select_all_state()
        } else {
          this.refresh_label_list_from_project()
        }

        if (this.mode == "multiple") {
          this.multiple = true
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

        selected_ids_only: function () {
          if (!this.selected || this.selected.length == 0) {
            return null
          }
          //single object
          if (this.selected.id) {
            return this.selected.id
          }
          // multiple
          // js errors if this.selected is not actually a list
          let ids_only = []
          for (let label_file of this.selected) {
            ids_only.push(label_file.id)
          }
          return ids_only
        }

      },
      data() {
        return {

          // we assume this to be false
          // unless updated by refreshing labels ie
          select_all_state: false,

          label_refresh_loading: false,
          selected: [],
          label_list: [],
          multiple: false,

          over_limit: false

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

              if (this.mode == "multiple") {

                this.refresh_internal_selected()

              }

              this.emit_selected()

              this.label_refresh_loading = false

            })
            .catch(error => {
              console.log(error);
            });

        },

        refresh_internal_selected: function () {

          // any label that comes up here is selected right?
          // because it's per group
          // not a fan that thsi component needs to know about groups but...

          // is there a better way we could be declaring this???... not great
          this.selected = []
          for (var label of this.label_list) {

            if (label.attribute_group_list) {
              for (var attribute of label.attribute_group_list) {

                if (attribute.id == this.attribute_group_id) {
                  this.selected.push(label)
                }
              }
            }

            if (this.load_selected_id_list) {
              // Added support to both objects and ID's
              for (let element of this.load_selected_id_list) {
                let id = element;
                // We assume we can be receiving a list of label objects, each ot them having an ID.
                if (!Number.isInteger(element)) {
                  id = element.id
                }
                if (label.id === id) {
                  this.selected.push(label)
                }
              }
            } else if (this.select_all_at_load == true) {
              this.selected = this.label_list
            }

          }


          this.check_select_all_state()


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
