<template>
  <div v-cloak id="labels_view">


      <v-layout row>
        <v-flex>

          <!-- TODO make max height the height of available space? -->
          <v-card style="overflow-y:auto; max-height: 700px" elevation="3">

            <v-card-title class="d-flex align-center">
              Label Templates

              <!-- New label -->
              <button_with_menu
                datacy="new_label_template"
                tooltip_message="New Label Template (Project Wide)"
                :large="true"
                v-if="show_edit_templates"
                @click="$store.commit('set_user_is_typing_or_menu_open', true)"
                @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
                icon="add"
                color="primary"
                :disabled="any_loading || view_only_mode || video_playing"
                offset="x"
              >

                <template slot="content">

                  <v_labels_new @label_created="on_label_created">
                  </v_labels_new>

                </template>

              </button_with_menu>


              <v-btn color="primary"
                     text
                     href="https://diffgram.readme.io/docs/create-your-first-label"
                     target="_blank"
                     icon>
                <v-icon>help</v-icon>
              </v-btn>

              <!-- For admins -->


              <!-- refresh_labels_function is called
                   on return because that updates the instance list /
                  attribute group information (for annotation use,
                  not managing it)-->

              <!-- The 'set_user_is_typing_or_menu_open' is for disabling hotkeys -->

              <!-- Attributes -->

              <!-- TODO, do we need min width? it seems to nicely detect it by itself...
                  min-width="600"
                  And do we event want or need a direction here?

                  [ ] is the new update return value working as expected?
                  -->

              <!-- Hide while WIP. TODO move to regular table -->
              <!--
              <v-text-field v-model="search"
                            append-icon="search"
                            @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                            @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                            label="Search"
                            single-line
                            hide-details></v-text-field>
              -->

              <tooltip_button
                v-if="show_create_samples"
                tooltip_message="Create Sample Labels"
                @click="open_sample_labels_dialog"
                icon="mdi-apps-box"
                :icon_style="true"
                :bottom="true"
                color="primary">
              </tooltip_button>

            </v-card-title>

            <v-alert type="info"
                     v-if="!loading && Labels.length == 0"
            >
              Welcome! Click the plus button to create your first label.
            </v-alert>

            <v_info_multiple :info="info"
                             @input="info = {}"
            >
            </v_info_multiple>
            <!-- Do we want this to keep popping back up after new creation?
                Not clear what rationale was for that-->

            <v-skeleton-loader
              :loading="any_loading"
              type="table"
              data-cy="skeletonloader"
            >

              <regular_table
                    :header_list="header_list"
                    :column_list="column_list"
                    datacy="labels_table"
                    :item_list="Labels"
                    :elevation="0"
                    ref="label_data_table"
                    @row_hover_index="table_row_hover_index = $event"
              >

                <template slot="label" slot-scope="props">

                  <v-layout>
                    <div v-if="props.item.colour != undefined" class="d-flex align-center">


                      <v-icon :style="style_color(props.item.colour.hex)"
                              class="clickable"
                              :disabled="video_playing"
                              @click="change_label_function(props.item)"
                      >flag
                      </v-icon>
                    </div>

                    <tooltip_icon
                      tooltip_message="Video Defaults to Single Frame"
                      v-if="props.item.label && props.item.label.default_sequences_to_single_frame"
                      icon="mdi-flag-checkered"
                      color="black">
                    </tooltip_icon>

                  <div v-if="props.item.id == current_label_file.id">

                    <v-badge v-if="view_only_mode != true &&
                          instance_type != 'tag'"
                              overlap
                              color="secondary"
                    >
                      <v-icon slot="badge">check</v-icon>
                    </v-badge>

                  </div>


                  <!-- Annotation Page Case -->
                  <v-btn :disabled="video_playing"
                          v-if="!show_edit_templates && current_label_file"
                          @click="change_label_function(props.item)"
                          text
                          style="text-transform: none !important;"
                          :color="props.item.id == current_label_file.id ? 'secondary' : 'primary' "
                  >
                    <h3 :data-cy="props.item.label.name">
                    {{ props.item.label.name }} </h3>
                  </v-btn>

                  <!-- Edit Page Case -->
                  <h3 v-else :data-cy="props.item.label.name"

                      >{{ props.item.label.name }}</h3>

                </v-layout>

              </template>

              <template slot="with_next_instance_buttons"
                        slot-scope="props"
                        >

                <div v-if="table_row_hover_index == props.index">
                  <tooltip_button

                    :disabled="loading"
                    @click="next_instance(props.item.id)"
                    icon="mdi-debug-step-over"
                    tooltip_message="Jump to Next Instance"
                    color="primary"
                    :icon_style="true"
                    :large="false"
                    :bottom="true"
                  >
                  </tooltip_button>
                </div>

              </template>

                  <!--
                  <td>
                    [category]
                  </td>
                  -->

                <template slot="show_visibility_toggle" slot-scope="props">

                  <v-layout>
                    <div v-if="table_row_hover_index == props.index
                         || props.item.is_visible == false">

                    <v-layout>

                      <div v-if="props.item.is_visible == true || props.item.is_visible == null">
                        <v-btn icon @click="toggle_label_visible(props.item)">
                          <v-icon color="blue">remove_red_eye</v-icon>
                        </v-btn>
                      </div>

                      <div v-if="props.item.is_visible == false">
                        <v-btn icon @click="toggle_label_visible(props.item)">
                          <v-icon color="grey">remove_red_eye</v-icon>
                        </v-btn>
                      </div>

                      <!--
                      <div v-if="$store.state.user.current.is_super_admin === true">
                        {{ props.item.id }}
                      </div>
                      -->

                    </v-layout>
                    </div>


                  </v-layout>

                </template>


                <!--
                There doesn't seem to be a good way to get sorted order still
                    so leave this until there is-->
                <!--
                <td>
                  <kbd>{{ props.index }} </kbd>
                </td>
                  -->

                <template slot="show_edit_templates" slot-scope="props">

                  <v-layout>

                    <!-- menu left ?-->

                    <button_with_menu
                      tooltip_message="Edit"
                      icon="edit"
                      :close_by_button="true"
                      v-if="view_only_mode != true && show_edit_templates"
                      @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
                      @click="$store.commit('set_user_is_typing_or_menu_open', true)"
                      color="primary"
                    >
                      <template slot="content">

                        <v_labels_edit :project_string_id="project_string_id"
                                        :label_file_prop="props.item"
                                        :edit_label_menu="edit_label_menu"
                                        :key="props.item.id"
                                        @request_boxes_refresh="$emit('request_boxes_refresh')">
                        </v_labels_edit>

                      </template>

                    </button_with_menu>


                    <button_with_menu
                      tooltip_message="Delete"
                      icon="delete"
                      :close_by_button="true"
                      color="primary"
                    >

                      <template slot="content">
                        <v-layout column>

                          <v-alert type="warning"
                          >
                            Existing instances with this label
                            will not be effected.
                          </v-alert>
                          <!-- TODO option to delete all assoicated instances? -->

                          <v-btn @click="api_file_update('REMOVE', props.item)"
                                  color="error"
                                  :loading="api_file_update_loading"
                                  :disabled="api_file_update_loading">
                            <v-icon>delete</v-icon>
                            Delete {{ props.item.label.name }}
                          </v-btn>

                        </v-layout>
                      </template>

                    </button_with_menu>

                  </v-layout>
                </template>

              </regular_table>

            </v-skeleton-loader>

          </v-card>

          <!--
          Only show on label main page
          as known bug about it refreshing-->

          <div class="pt-4" v-if="show_attributes_table">
            <v-card>
              <attribute_home :project_string_id="project_string_id">

              </attribute_home>
            </v-card>
          </div>
          <!--
           Move attributes to be more visible to help reduce confusion.
          -->

          <v-card v-if="show_edit_templates">
            <v-alert type="info"
                     dismissible
            >
              Once Tasks are launched the labels for those Tasks are "locked" by default.
            </v-alert>

          </v-card>

        </v-flex>
      </v-layout>

    <v-dialog v-model="dialog_confirm_sample_data" max-width="450px">
      <v-card >
        <v-card-title class="headline">
          Create sample data
        </v-card-title>
        <v-card-text>
          Do you want to create sample labels?
          This will add 3 sample labels to the project.
        </v-card-text>
        <v_error_multiple :error="error_sample_data">
        </v_error_multiple>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary darken-1"
            text
            @click="dialog_confirm_sample_data = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="success darken-1"
            text
            :loading="loading_create_sample_data"
            @click="create_sample_labels"
          >
            Create Sample Labels
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="snackbar_success"
      :timeout="3000"
      color="primary"
    >
      Sample data created successfully.

      <template v-slot:action="{ attrs }">
        <v-btn
          color="white"
          text
          v-bind="attrs"
          @click="snackbar_success = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>

  </div>
</template>

<script lang="ts">

  import axios from '../../services/customInstance';
  import attribute_home from '../attribute/attribute_home'


  import Vue from "vue";

  export default Vue.extend({
      name: 'labels_view',

      components: {
        attribute_home
      },

      /*
       * TODO
       * Switch to each "sub part" simply declares if it's rendered or now,
       * NOT having to know about a
       * "mode" since then it has to know about the context in which it's being used!!!
       * ie "render_attributes" : { default: true}
       */

      props: {
        'project_string_id': {},
        'with_next_instance_buttons': {
          default: false
        },
        'current_video_file_id': {},
        'annotation_assignment_on': {},
        'render_mode': {
          default: 'own_page'
        },
        'loading': {},
        'show_edit_templates': {
          default: false
        },
        'show_create_samples': {
          default: false
        },
        'request_label_file_refresh': {
          default: true
        },
        'change_label_from_id': {},
        'video_mode': {},
        'view_only_mode': {},
        'instance_type': {},
        'push_label_file_colour_map': {
          default: null
        },
        'push_label_list': {
          default: null
        },
        'show_attributes_table': {
          default: false
        },
        'show_visibility_toggle': {
          default: false
        },
        'task': {
          default: null
        },
        'video_playing': {
          default: null
        }

      },
      watch: {
        loading: function (bool) {
          // this is used to detect change from parent loading
          this.loading_prop = bool
        },
        request_label_file_refresh: function (bool) {
          if (bool == true) {
            this.refresh_labels_function()

          }
        },
        change_label_from_id: function (label_id) {
          this.change_label_from_id_function(label_id)
        },
        push_label_list: function () {

          if (this.push_label_list == null) {
            return
          }

          this.label_file_colour_map = this.push_label_file_colour_map
          this.Labels = this.push_label_list
          this.label_refresh_loading = false

          // This will also trigger sequence refresh
          this.change_label_function(this.Labels[0])
        }
      },
      beforeMount() {

      },
      mounted() {
        /*
          Label refresh process
          Two methods to *trigger* refresh labels
          a) setting props,  :request_label_refresh="true"

          this method works best for default page load conditions
          and components that directly embed it

          b) calling  this.$store.commit('init_label_refresh')

          better in that case to simple call `this.$store.commit('init_label_refresh')`
          `this.$store.commit('finish_label_refresh')` is automatically called at end
          of refresh, and also works to "reset" state to false
        */

        if (this.request_label_file_refresh == true) {
          this.refresh_labels_function()
        } else {
          this.label_refresh_loading = false
        }

        var self = this
        this.label_watcher = this.$store.watch((state) => {
            return this.$store.state.labels.refresh
          },
          (new_val, old_val) => {
            if (new_val == true) {
              self.refresh_labels_function()
            }
          },
        )

        window.addEventListener('keyup', this.keyboard_events_window);

        // Reset this just in case something gets messed up with store
        this.$store.commit('set_user_is_typing_or_menu_open', false)

      },

      beforeDestroy() {
        window.removeEventListener('keyup', this.keyboard_events_window)
      },
      destroyed() {
        this.label_watcher()
        this.info = {}
      },
      data() {
        return {

          table_row_hover_index: -1,

          options: {
            'itemsPerPage': -1,
            'sortBy': ['label.name'],  // match value, not column name
            'sortDesc': [false]  // ascending
          },

          colour: {
            hex: '#194d33',
            hsl: {h: 150, s: 0.5, l: 0.2, a: 1},
            hsv: {h: 150, s: 0.66, v: 0.30, a: 1},
            rgba: {r: 25, g: 77, b: 51, a: 1},
            a: 1
          },

          api_file_update_loading: false,
          snackbar_success: false,
          dialog_confirm_sample_data: false,
          loading_create_sample_data: false,
          error_sample_data: {},
          header_list: [
            {
              text: "Name",
              align: 'left',
              value: "label.name",
              header_string_id: 'label',
              width: "250px",
              fixed: true
            },
            {
              text: "Next Instance",
              align: 'left',
              sortable: false,
              value: null,
              header_string_id: 'with_next_instance_buttons',
              width: "75px",  // prevents it jerking when on hover happens
              fixed: true
            },
            {
              text: "Visibility",
              align: 'left',
              sortable: false,
              value: null,
              header_string_id: 'show_visibility_toggle',
              width: "75px",
              fixed: true
            },
            {
              text: "Actions",
              align: 'left',
              sortable: false,
              value: null,
              header_string_id: 'show_edit_templates'
            }
          ],
          info: {},

          edit_label_menu: false,

          search: "",

          label_search: null,

          label_refresh_loading: true,
          loading_prop: false,

          new_label: false,
          error_name: null,

          label_file_colour_map: {},

          label_warning: false,
          current_label_file: {
            id: null
          },

          Labels: [], // TODO rename to label_list if possible

          rules: {
            required: (value) => !!value || 'Required.',
          },

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

          expanded_once: false

        }
      },

      computed: {
        column_list: function () {

          let _column_list = [
            "label"]

          if(this.$props.with_next_instance_buttons){ // maintain order, must match physical structure
            _column_list.splice(1, 0, 'with_next_instance_buttons')
          }
          if(this.$props.show_visibility_toggle){
            _column_list.push('show_visibility_toggle')
          }
          if(this.$props.show_edit_templates){
            _column_list.push('show_edit_templates')
          }
          return _column_list
        },
        any_loading: function () {
          return this.loading_prop || this.label_refresh_loading
        }
      },

      methods: {
        open_sample_labels_dialog: function(){
          this.dialog_confirm_sample_data = true;
        },
        create_sample_labels: async function(){
          this.loading_create_sample_data = true;
          try{
            const response = await axios.post('/api/walrus/v1/project/' + this.$store.state.project.current.project_string_id + '/gen-data', {
              data_type: 'label'
            })
            if(response.status === 200){
              this.refresh_labels_function();
              this.dialog_confirm_sample_data = false;
              this.snackbar_success = true;
            }
          }
          catch (error) {
            this.error_sample_data = this.$route_api_errors(error);
          }
          finally {
            this.loading_create_sample_data = false;
          }
        },
        on_label_created: function (label) {
          this.$emit('label_created', label);
        },
        expand_once: function () {

          /* It's unclear where to trigger this
           * For example, changing the file should trigger it,
           * Maybe on current_video_file_id or something,
           * BUT still the issue that trigging this doesn't seem to cause the component in the slot load as expected
           * As a (seperate?) concern, closing expanded stuff, if person clicks on an image file after
           * So better to still wait on  https://github.com/vuetifyjs/vuetify/pull/5737
           * Tried    <div v-if="expand_once()">
                        </div> too - not the right spot / expected behaviour
           */

          // very hacky
          if (this.video_mode != true) {

            // case of loading a video file
            // then loading an image
            /*
            if (this.expand_once == true) {
              for (label in this.Labels) {
                this.$set(this.$refs.label_data_table.expanded,
                  label.id,
                  false)
              }
            }
            */
            this.expanded_once = false // reset
            return
          }

          if (this.expanded_once == false) {
            this.expanded_once = true
            this.$set(this.$refs.label_data_table.expanded,
              this.Labels[0].id,
              true)
          }


        },

        // From back when we had sequence thing embedded in data table
        /*
        show_sequence: function (expanded) {

          if (this.video_mode == true) {
            return !expanded
          }
          else {
            return expanded
          }
        },
        */

        attribute_menu_close() {

          this.refresh_labels_function()
          this.$store.commit('set_user_is_typing_or_menu_open', false)
        },

        style_color: function (hex) {
          return "color:" + hex
        },

        refresh_labels_function: function () {
          /*
         Label refresh process
         Two methods to *access* refresh labels
         a) project id

         b) annotation_project id

       */
          if (this.project_string_id == null) {
            return
          }

          var url = null
          this.label_refresh_loading = true

          if (['full', 'home', 'own_page'].includes(this.render_mode) == true) {
            url = '/api/project/' + this.project_string_id + '/labels/refresh'
          }

          axios.get(url, {})
            .then(response => {

              this.Labels = response.data.labels_out

              this.label_file_colour_map = response.data.label_file_colour_map
              this.$emit('label_file_colour_map', this.label_file_colour_map)
              this.$emit('label_list', this.Labels)

              if (this.Labels[0] != null && !this.show_edit_templates) {  // default to first label
                this.change_label_function(this.Labels[0])
              } else {
                // TODO review this
                //this.label_warning = true
              }


              this.label_refresh_loading = false
              this.$emit('request_label_refresh_callback', true)
              this.$store.commit('finish_label_refresh')


              //this.Labels[0].is_active = true;

            })
            .catch(error => {
              console.error(error);
            });

        },
        change_label_from_id_function: function (label_id) {
          for (let i in this.Labels) {
            if (this.Labels[i] && label_id == this.Labels[i].id) {
              this.change_label_function(this.Labels[i])
            }
          }

        },
        change_label_function: function (label) {
          if (this.show_edit_templates) {
            return
          }
          /*
           *  This will also trigger sequence refresh
           *  because it pushes label to annotation core
           *  and sequence list is watching annotation core (label_file_id)
           *  we can commit to sequence_refresh to force it
           *  ie this.$store.commit('sequence_refresh', Date.now())
           *  but it won't really do it as expected since we want the label file anyway here
           */

          // generally we expect that the label we emit
          // is valid so lets reject invalid labels here?
          if (label == undefined) {
            return
          }

          if (this.video_playing == true) {
            return
          }

          this.current_label_file = label
          this.$emit('change_label_file_function', label)


        },
        keyboard_events_window: function (event) {


          // hotkeys

          // is actually generic open menu lock
          if (this.$store.state.user.is_typing_or_menu_open == true) {
            return
          }

          let hotkey = null
          hotkey = this.hotkey_dict[event.keyCode]
          if (hotkey != null) {
            this.change_label_function(this.Labels[hotkey])
          }

        },

        api_file_update(mode, label) {

          this.api_file_update_loading = true
          this.info = {}  // reset

          axios.post('/api/v1/project/' + this.project_string_id
            + '/file/update',
            {
              'file_list': [label],
              'mode': mode
            })
            .then(response => {


              this.refresh_labels_function()
              this.info = response.data.log.info

              if (mode == "REMOVE") {

                // Case of removing last label file / not relying on refresh to clear it
                this.current_label_file = {
                  id: null
                }
                this.$emit('change_label_file_function', this.current_label_file)

              }

              this.api_file_update_loading = false

            }).catch(e => {
            console.error(e)
            this.api_file_update_loading = false

          })

        },

        toggle_label_visible(label) {
          // careful must use splice method

          if (typeof label.is_visible == "undefined") {
            label.is_visible = false
          } else {
            label.is_visible = !label.is_visible
          }
          this.Labels.splice(this.Labels.indexOf(label), 1, label)
          this.$emit('update_label_file_visible', label)
        },
        next_instance(label_name){
          this.$emit('get_next_instance', label_name)
        }
      }
    }
  ) </script>


<style>
  .v-data-table__wrapper{
    overflow: visible !important;
  }
</style>
