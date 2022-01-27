<template>
  <div v-cloak>
    <v-alert type="success"
             class="ma-0"
             :value="focus_mode">
      In focus mode.
      <v-btn @click="show_all()">
        Exit
      </v-btn>
    </v-alert>
    <v-layout row>
      <div v-if="render_mode=='gold_standard'">Gold standard instances</div>


      <global_attributes_list
        :global_attribute_groups_list="global_attribute_groups_list"
        :current_global_instance="current_global_instance"
        :view_only_mode="view_only_mode"
        @attribute_change="global_attribute_change($event)"
      ></global_attributes_list>

      <v-divider v-if="attribute_group_list_prop.length != 0"></v-divider>

      <v-expansion-panels
        v-if="attribute_group_list_prop.length != 0"
        v-model="instance_detail_open"
        accordion
        flat
      >
        <v-expansion-panel>

          <v-expansion-panel-header class="d-flex justify-start pa-0 sidebar-accordeon-header align-center">

            <v-icon left class="ml-5 flex-grow-0" color="primary" size="18">
              mdi-selection
            </v-icon>

            <h4>Selection</h4>

            <v-spacer></v-spacer>

            <v-chip x-small class="d-flex justify-center flex-grow-0">
              {{ attribute_group_list_prop.length }}
            </v-chip>
          </v-expansion-panel-header>

          <v-expansion-panel-content>

            <attribute_group_list
              style="overflow-y:auto; max-height: 400px"
              v-if="attribute_group_list_prop.length != 0"
              :mode=" 'annotate' "
              :view_only_mode="view_only_mode"
              :attribute_group_list_prop="attribute_group_list_prop"
              :current_instance="current_instance"
              @attribute_change="attribute_change($event)"
              key="attribute_groups_list"
            >
            </attribute_group_list>


          </v-expansion-panel-content>

        </v-expansion-panel>
      </v-expansion-panels>


      <v-expansion-panels accordion flat v-model="panels">
        <v-expansion-panel v-for="grouped_list in filtered_instance_set" >

          <v-expansion-panel-header class="d-flex justify-start pa-0 sidebar-accordeon-header" v-if="grouped_list.model_run">

              <strong v-if="grouped_list.model_run.id !== -1">
                <v-icon  class="ml-5 flex-grow-0" color="primary" size="18" :color="grouped_list.model_run.color">mdi-group</v-icon>
                <h4 class="ml-4">{{ grouped_list.model_run.reference_id }}</h4>
              </strong>
              <strong v-if="grouped_list.model_run.id === -1">
                <v-icon  class="ml-5 flex-grow-0" size="18" color="secondary">mdi-group</v-icon>
                <h4 class="ml-4">Ground Truth:</h4>
              </strong>
              <v-btn class="d-flex justify-center flex-grow-0" icon small v-on:click.stop="focus_model_run(grouped_list.model_run)">
                <v-icon v-if="current_model_run_filter && (current_model_run_filter.id === grouped_list.model_run.id)"
                        color="secondary">mdi-eye
                </v-icon>
                <v-icon v-if="!current_model_run_filter" color="primary">mdi-eye</v-icon>
                <v-icon v-if="current_model_run_filter && (current_model_run_filter.id !== grouped_list.model_run.id)"
                        color="primary">mdi-eye
                </v-icon>
              </v-btn>
          </v-expansion-panel-header>

          <v-expansion-panel-header class="d-flex justify-start pa-0 pb-2 sidebar-accordeon-header align-center">

            <v-icon left class="ml-5 flex-grow-0" color="primary" size="18">
              mdi-brush
            </v-icon>

            <h4 class="ml-0">Annotations</h4>

            <v-spacer></v-spacer>
            <v-chip x-small v-if="instance_list_count > 0" class="d-flex justify-center flex-grow-0">
              {{ instance_list_count }}
            </v-chip>

          </v-expansion-panel-header>

          <v-expansion-panel-content class="ml-2">
            <v-chip v-if="current_instance
                      && current_instance.id
                      && $store.state.user.current.is_super_admin == true" x-small class="ma-2" color="secondary">
              <span class="font-weight-bold mr-2">Selected: </span> <span>{{ current_instance.id }}</span>
            </v-chip>
            <v-data-table v-if="grouped_list &&
                                    grouped_list.instance_list.length > 0"
                          style="overflow-y:auto; max-height: 450px"
                          :headers="header"
                          :items="grouped_list.instance_list"
                          :search="search"
                          class="elevation-1"
                          item-key="id"
                          v-model="selected"
                          hide-default-footer
                          :options.sync="options"
                          ref="instance_data_table">

              <template slot="item" slot-scope="props">

                <!-- v-if="props.item.soft_delete != true" -->

                <tr v-if="props.item.soft_delete != true
                  || label_settings.show_removed_instances == true"
                    @mouseover="data_table_hover_index=props.item.instance_list_index"
                    @mouseleave="data_table_hover_index=-1"
                >

                  <td v-if="render_mode == 'file_diff'">

                    <div v-if="props.item.change_type=='added'">
                      <v-icon color="green">add_circle</v-icon>
                    </div>

                    <div v-if="props.item.change_type=='deleted'">
                      <v-icon color="red">remove_circle</v-icon>
                    </div>

                    <div v-if="props.item.change_type=='unchanged'">
                      <v-icon color="grey">fiber_manual_record</v-icon>
                    </div>
                  </td>

                  <td>

                    <v-layout>


                      <!-- TODO error handling here -->
                      <div class="color-box"
                           @click="change_instance(props.item, props.item.instance_list_index),show_all()"
                           v-if="label_file_colour_map[props.item.label_file_id]">

                        <div v-if="props.item.type =='box'">
                          <v-icon :style="get_instance_color(props.item)">
                            mdi-checkbox-blank
                          </v-icon>
                        </div>

                        <div v-if="props.item.type=='keypoints'">
                          <v-icon :style="get_instance_color(props.item)">
                            mdi-vector-polyline
                          </v-icon>
                        </div>

                        <div v-if="props.item.type=='polygon'">
                          <v-icon :style="get_instance_color(props.item)">
                            mdi-vector-polygon
                          </v-icon>
                        </div>

                        <div v-if="props.item.type=='tag'">
                          <v-icon :style="get_instance_color(props.item)">
                            mdi-tag
                          </v-icon>
                        </div>

                        <div v-if="props.item.type=='line'">
                          <v-icon :style="get_instance_color(props.item)">
                            mdi-minus
                          </v-icon>
                        </div>

                        <div v-if="props.item.type=='point'">
                          <v-icon :style="get_instance_color(props.item)">
                            mdi-circle-slice-8
                          </v-icon>
                        </div>


                        <!--  1) :color="null"  otherwise it overrides the style!
                              2) using style not color becuase vuetify seems to only support "named" colors-->

                        <tooltip_icon
                          tooltip_message="Cuboid"
                          v-if="props.item.type == 'cuboid'"
                          icon="mdi-cube-outline"
                          :icon_style="get_instance_color(props.item)">
                        </tooltip_icon>

                        <tooltip_icon
                          tooltip_message="Cuboid"
                          v-if="props.item.type == 'cuboid_3d'"
                          icon="mdi-cube-outline"
                          :icon_style="get_instance_color(props.item)">
                        </tooltip_icon>

                        <tooltip_icon
                          tooltip_message="Ellipse"
                          v-if="props.item.type == 'ellipse'"
                          icon="mdi-ellipse-outline"
                          :icon_style="get_instance_color(props.item)">
                        </tooltip_icon>

                        <tooltip_icon
                          tooltip_message="Curve"
                          v-if="props.item.type == 'curve'"
                          icon="mdi-chart-bell-curve-cumulative"
                          :icon_style="get_instance_color(props.item)">
                        </tooltip_icon>
                        <v-chip x-small v-if="$store.state.user.current.is_super_admin == true">
                          ID: {{ props.item.id }}
                        </v-chip>
                        <v-chip v-if="props.item.soft_delete == true"
                                color="red"
                                small
                                text-color="white"
                        >
                          Removed
                        </v-chip>

                      </div>

                      <!-- Sequence info & color -->
                      <div>
                        <v-chip v-if="props.item.sequence_id"
                                :color="$get_sequence_color(props.item.sequence_id)"
                                text-color="white"
                                @click="change_instance(props.item, props.item.instance_list_index),show_all()"
                                class="pa-2"
                                small
                        >
                          <span style="font-size: 12px;"> {{ props.item.number }}</span>

                        </v-chip>
                      </div>

                      <!-- More clarity on instance "source"
                        ie human made, machine made, etc.-->

                      <!-- Interpolated -->
                      <tooltip_icon
                        tooltip_message="Interpolated"
                        v-if="props.item.interpolated &&
                              props.item.interpolated == true"
                        icon="filter_none"
                        color="primary"
                      >
                      </tooltip_icon>

                      <tooltip_icon
                        tooltip_message="Machine Made"
                        v-if="props.item.machine_made &&
                              props.item.machine_made == true"
                        icon="mdi-memory"
                        color="primary"
                      >
                      </tooltip_icon>

                      <tooltip_icon
                        tooltip_message="Human Made"
                        v-if="!props.item.machine_made"
                        icon="mdi-account"
                        color="primary"
                      >
                      </tooltip_icon>

                    </v-layout>

                  </td>

                  <td style="max-width: 140px; position: relative">
                    <!-- Full item comparison because
                        new objects won't have id-->

                    <div
                      v-if="current_instance.creation_ref_id != undefined && props.item.creation_ref_id == current_instance.creation_ref_id"
                      style="position: absolute; right: 0; top: 0">

                      <v-badge v-if="view_only_mode != true"
                               overlap
                               color="secondary"
                      >
                        <v-icon dark slot="badge">check</v-icon>
                      </v-badge>

                    </div>

                    <div v-if="props.item.label_file &&
                                   props.item.label_file.label">

                      <!-- Context, when a user focuses an instance, we expect it to select it
                           However, when a user *just* selects an instance, we expect it to lose focus-->
                      <span
                        :style="style_instance_selected_color(props.item)"
                        @click="change_instance(props.item, props.item.instance_list_index),
                               show_all()">
                            {{ props.item.label_file.label.name }}
                          </span>
                    </div>


                  </td>


                  <!-- Focus mode toggle -->
                  <td>

                    <div v-if="props.item.type != 'tag'
                     && render_mode != 'gold_standard'
                     ">
                      <div v-if="data_table_hover_index == props.item.instance_list_index
                          || instance_focused_index == props.item.instance_list_index
                       ">

                        <v-btn @click="toggle_instance_focus(props.item.instance_list_index, props.item.id)"
                               icon
                        >
                          <v-icon v-if="instance_focused_index == props.item.instance_list_index"
                                  size="18"
                                  color="blue">remove_red_eye
                          </v-icon>

                          <v-icon v-if="instance_focused_index != props.item.instance_list_index"
                                  size="18"
                                  color="gray">remove_red_eye
                          </v-icon>
                        </v-btn>
                      </div>
                      <!-- TODO better handling of focus mode
                         (We do want to use it in gold standard mode too)
                           Do we want to limit to one at a time?
                          Or each click simply puts on / off for that specific instance?
                          Confusing if it works differently from labels-->
                      <!--
                      <v-btn v-if=""
                             icon @click="toggle_instance_focus(props.item.instance_list_index, props.item.id)">
                        <v-icon color="grey">remove_red_eye</v-icon>
                      </v-btn>
                          -->
                    </div>

                  </td>

                  <!-- Actions -->
                  <td v-if="!view_only_mode && !anonymous_user_in_public_project">
                    <v-layout>

                      <!-- Edit label
                         For images only
                        -->
                      <div v-if="data_table_hover_index == props.item.instance_list_index
                        || data_table_inner_menu_open == true
                        && data_table_hover_click_index == props.item.instance_list_index ">
                        <button_with_menu
                          v-if="video_mode != true"
                          @menu_open="data_table_inner_menu_open = $event,
                                  data_table_hover_click_index=props.item.instance_list_index"
                          tooltip_message="Change Label Template"
                          icon="mdi-format-paint"
                          color="primary"
                          :close_by_button="true"
                        >

                          <template slot="content">
                            <v-layout column>

                              <label_select_only
                                :label_file_list_prop=label_list
                                :select_this_id_at_load=props.item.label_file_id
                                @label_file="instance_update(
                                            'update_label',
                                             props.item.instance_list_index,
                                             props.item.id,
                                             'default',
                                             $event)"
                              >
                              </label_select_only>


                            </v-layout>
                          </template>

                        </button_with_menu>
                      </div>

                      <div v-if="data_table_hover_index == props.item.instance_list_index">
                        <v-btn v-if="!view_only_mode
                         && props.item.soft_delete == true"
                               @click="instance_update('delete_undo', props.item.instance_list_index, props.item.id)"
                               icon>
                          <v-icon> undo</v-icon>
                        </v-btn>

                        <!-- Prob need to set this as a flag and move to application logic at this point -->

                        <v-btn v-if="render_mode != 'gold_standard'
                          && ((task && task.task_type != 'review') || current_file)
                          && !view_only_mode
                          && props.item.soft_delete != true"
                               @click="instance_update('delete', props.item.instance_list_index, props.item.id)"
                               icon>
                          <v-icon size="18"> delete</v-icon>
                        </v-btn>
                      </div>


                      <!-- Review and gold standard stuff -->

                      <rating_review v-if="task && task.task_type == 'review' && render_mode != 'gold_standard' "
                                     :rating_prop="props.item.rating"
                                     @rating_update="instance_update(
                                                    'rating_update',
                                                    props.item.instance_list_index,
                                                    props.item.id,
                                                    'default',
                                                    $event)">
                        <!-- $event has rating value -->
                      </rating_review>


                      <!-- Should we use a toggle switching instead or? -->
                      <!-- A toggle switch is tough to use here
                     since v-model="props.item.missing" assumes all the gold standard ones
                     have it set to false by default? -->

                      <v-layout v-if="render_mode == 'gold_standard'">
                        <v-btn @click="instance_update('toggle_missing',
                                       props.item.instance_list_index,
                                       props.item.id,
                                       'gold_standard')"
                               :disabled="props.item.missing"
                               color="primary"
                        >
                          Missing
                        </v-btn>

                        <v-btn @click="instance_update('toggle_missing',
                                       props.item.instance_list_index,
                                       props.item.id,
                                       'gold_standard')"
                               color="primary"
                               icon
                               text
                        >
                          <v-icon> undo</v-icon>
                        </v-btn>
                      </v-layout>
                    </v-layout>
                  </td>

                  <!-- End Actions -->


                </tr>


              </template>

              <v-alert slot="no-results" color="error" icon="warning">
                Your search for "{{ search }}" found no results.
              </v-alert>

            </v-data-table>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>

      <v-alert type="warning"
               :value="label_settings.show_removed_instances == true">
        Showing removed.
      </v-alert>

    </v-layout>


  </div>
</template>

<script lang="ts">

import rating_review from './rating_review'
import attribute_group_list from '../attribute/attribute_group_list.vue';
import label_select_only from '../label/label_select_only.vue'
import global_attributes_list from '../attribute/global_attributes_list'
import Vue from "vue";

export default Vue.extend({
    name: 'instance_detail_list',
    components: {
      rating_review,
      attribute_group_list,
      label_select_only,
      global_attributes_list
    },
    // TODO defaults with dicts here
    props: [
      'task',
      'draw_mode',
      'instance_list',
      'label_file_colour_map',
      'model_run_list',
      'refresh',
      'view_only_mode',
      'label_settings',
      'label_list',  // label_file_list
      'video_mode',
      'current_frame',  // number
      'current_video_file_id',  // strange only seem to have id
      'current_label_file_id',
      'video_playing', // bool
      'external_requested_index', // number
      'trigger_refresh_current_instance',  // null or Date.now()  number,
      'current_file',
      'global_attribute_groups_list',
      'current_global_instance'

    ],
    watch: {
      instance_list: function ($event) {

        // but if say instance list changes or other fall back selects we do care about this ongoing basis
        this.determine_if_should_change_instance($event)
        this.set_instance_index_numbers();

      },

      video_playing: function () {

        // context of catching that "last one" when video is playing
        // not super clear if this is a good idea
        if (this.video_playing == false) {
          this.determine_if_should_change_instance()
        }

      },

      trigger_refresh_current_instance: function () {
        if (this.instance_list) {
          this.change_instance(
            this.instance_list[this.external_requested_index],
            this.external_requested_index)
        }

      },

      current_file: function () {
        if (!this.current_file) {
          return
        }
        if (this.video_mode == true) {
          return
        }

        if (this.prior_file_id == this.current_file.id) {
          return
        }

        this.prior_file_id = this.current_file.id

        this.change_instance({}, null)
        this.prior_instance_list_length = null

      }

    },
    mounted() {
      this.set_instance_index_numbers()
    },
    data() {
      return {

        openedGlobalPanel: 0,
        instance_detail_open: true,
        current_global_instance_index: 0, // hard coded until support multiple

        render_mode: "deprecated",  // pending moving gold standard to it's own component if needed (moving shared functions to general JS object)

        data_table_hover_index: -1,
        data_table_hover_click_index: -1,
        data_table_inner_menu_open: false,

        first_instance_load: true,
        focus_mode: false,
        instance_focused_index: null,

        prior_instance_list_length: null,
        prior_current_frame: null,
        prior_current_video_file_id: null,
        prior_file_id: null,

        search: "",

        panels: 0,
        selected: [],

        // Caution, this current_instance concept is different from the one in
        // annotation core. here it's the "selected" one,
        // there it's the one actively being drawn
        current_instance: {},
        current_instance_index: null,
        current_model_run_filter: null,

        options: {
          'sortBy': ['column1'],
          'sortDesc': [true],
          'itemsPerPage': -1
        },

        // TODO handle sort mapping
        base_header: [
          {
            text: "Type",
            align: 'left',
            sortable: false,
            value: 'type'
            //width: "1%"
          },
          {
            text: "Name",
            align: 'left',
            sortable: false,
            value: "label_file.label.name",
            width: "100px",
            fixed: true
          },
          {
            text: "Focus",
            align: 'left',
            sortable: false,
            value: null,
            width: "75px",  // prevents it jerking when on hover happens
            fixed: true
          },
          {
            text: "Actions",
            align: 'left',
            sortable: false,
            value: null,
            width: "150px",
            fixed: true
          }
        ]


      }

    },

    computed: {


      anonymous_user_in_public_project: function () {
        if (this.$store.getters.is_on_public_project && !this.$store.state.user.logged_in) {
          return true
        } else {
          return false;
        }
      },
      instance_list_count: function () {
        let count = 0;
        for (const group of this.filtered_instance_set) {
          if (this.label_settings.show_removed_instances) {
            count += group.instance_list.length;
          } else {
            count += group.instance_list.filter(inst => inst.soft_delete === false).length;
          }

        }
        return count
      },
      filtered_instance_set: function () {
        const instance_list = this.instance_list.map((inst, i) => ({
          ...inst,
          instance_list_index: i
        })).filter(elm => elm.type !== 'global')
        if (this.model_run_list && this.model_run_list.length > 0) {
          const result = [];
          for (const model_run of this.model_run_list) {
            const new_instance_list = this.instance_list.filter(inst => inst.model_run_id === model_run.id);
            result.push({
              instance_list: new_instance_list,
              model_run
            })

          }
          // Add Ground Truth
          result.push({
            model_run: {id: -1}, // Assume -1 Id for ground truth instances.
            instance_list: this.instance_list.filter(inst => !inst.model_run_id)
          })
          return result;

        } else {
          return [
            {
              model_run: null,
              instance_list
            }
          ]
        }

      },
      attribute_group_list_prop: function () {

        // attribute_group_list_prop handles determining which group it
        // should passed based on current label

        if (!this.label_list
          || !this.current_instance
          || !this.current_instance.label_file) {
          return []
        }

        for (var label of this.label_list) {

          if (this.current_instance.label_file_id == label.id) {
            return label.attribute_group_list

          }
        }
        return []

      },

      header: function () {
        if (this.render_mode == 'file_diff') {

          let change_type = {
            text: "Type",
            align: 'left',
            sortable: false,
            value: 'label.change_type'
          }
          this.base_header.unshift(change_type)
          return this.base_header

        }
        if (this.task && this.task.task_type == 'review' && this.render_mode != "gold_standard") {
          // This is really brittle but works for now
          this.base_header[3].width = "600px"
        }
        if (this.view_only_mode && this.anonymous_user_in_public_project) {
          for (let i = 0; i < this.base_header.length; i++) {
            const header = this.base_header[i];
            if (header.text === 'Actions') {
              this.base_header.splice(i, 1);
            }
          }
          return this.base_header
        } else {

          return this.base_header
        }
      },

      header_colour: function () {
        if (this.render_mode == "gold_standard") {
          return "#FFD700"
        }
        return "white"
      }

    },
    methods: {
      set_instance_index_numbers: function () {
        for (let i = 0; i < this.instance_list.length; i++) {
          this.instance_list[i].instance_list_index = i;
        }
      },
      get_next_instance_index_from_sequence: function (number, label_file_id) {
        const indexes = [];
        for (let i = 0; i < this.instance_list.length; i++) {
          if (this.instance_list[i].soft_delete) {
            continue
          }
          if (this.instance_list[i].label_file_id != label_file_id) {
            continue
          }
          if (this.instance_list[i].number === number) {
            indexes.push(i);
          }
        }
        if (indexes.length === 1) {
          return indexes[0]
        } else {
          return null;
        }
      },
      determine_if_should_change_instance: function (instance_list_new) {
        /*
         *
         * See https://docs.google.com/document/d/1EVvPke7Ms25KsmDKpwrQcqB1k6pgB5SNs5WDbwGmLCo/edit#heading=h.3kp2xdv2h899
         * Assumes the last element in the list is the most recent instance added
         *
         * Other way we could do it is DECLARE when creating a
         * new instance but that wouldn't help for say file changes right.
         *
         * Perhaps in general the biggest concern is for new instances
         * and then thinking about just visibility, ie to make sure on the right one
         * /exepcted one
         *
         * It's jarring if it changes while say clicking the attribute stuff...
         * It's a sort of strange problem. It feels like we should be able
         * to say use the instance id. But what if there is no instance id?
         * Also what if the instance id changes? hmmm
         *
         *
         *
         *   Instance delete case, instance list does not change
         *
         *   We could fix this downsteam in terms of the "selected" instance
         *   Could also have a date time thats like "force refresh" or something
         */


        if (this.$props.video_playing == true) {
          return
        }
        if (!this.$props.instance_list) {
          return
        }

        if (this.$route.query.instance &&
          this.first_instance_load == true) {
          // Default, assuming we don't have a query thing
          // a challenge here is this function is used elsewhere too...
          // and only care about this on first load....
          this.change_instance_from_id(this.$route.query.instance)
          this.first_instance_load = false

          return
        }


        if (this.instance_list && this.instance_list.length == 0) {
          this.change_instance({}, null)
          return
        }

        if (this.video_mode == false) {
          return
        }


        // Case of changing frame number

        if (this.prior_current_frame != undefined && this.current_frame != undefined
          && this.prior_current_frame != this.current_frame) {
          if (this.current_instance.number != undefined) {
            const instance_index = this.get_next_instance_index_from_sequence(
              this.current_instance.number,
              this.current_instance.label_file_id)

            if (instance_index != undefined) {
              // We want the instance to be selected too.
              // Not 100% sure if we should do this, so pending review.

              this.instance_list[instance_index].selected = true;
              this.current_instance.selected = false;

              this.change_instance(this.instance_list[instance_index], instance_index)
            } else {
              // Fallback if there is no instance with the same sequence
              this.change_instance({}, null)
            }
          } else {
            // Default case if no sequence available
            this.change_instance({}, null)
          }
          // update to monitor if anything changes.
          this.prior_instance_list_length = this.instance_list.length
          this.prior_current_frame = this.current_frame
          this.prior_current_video_file_id = this.current_video_file_id

        }
          // Default case, ie creating new instances
        // Applies to both images and video
        else if (this.prior_instance_list_length != this.instance_list.length ||
          this.prior_current_video_file_id != this.current_video_file_id) {
          // Default case, randomly take last element
          // there may be no instances that match current label file.
          let index = this.instance_list.length - 1

          // Context is changing frames, we want to "stick" with the selected instance

          if (this.current_label_file_id &&
            this.current_file.id != this.prior_file_id) {

            let stick_with_label_file_index = this.instance_list.findIndex(instance => {
              return instance.label_file_id == this.current_label_file_id &&
                instance.soft_delete != true
            })

            // not found case
            if (stick_with_label_file_index != -1) {
              // future perhaps we may want this to be null then...
              index = stick_with_label_file_index
            }
          }
          // arguments are object and index
          this.change_instance(this.instance_list[index], index)

          // update to monitor if anything changes.
          this.prior_instance_list_length = this.instance_list.length
          this.prior_current_frame = this.current_frame
          this.prior_current_video_file_id = this.current_video_file_id

          return
        }

        for (let i = 0; i < this.instance_list.length; i++) {
          this.instance_list[i].instance_list_index = i;
        }

      },

      attribute_change: function (attribute) {
        this.instance_update(
          "attribute_change",
          this.current_instance_index,
          this.current_instance.id,
          "default",
          attribute
        )

      },

      global_attribute_change: function (attribute) {

        this.instance_update(
          "attribute_change",
          this.current_global_instance_index,
          this.current_global_instance.id,
          "global",
          attribute
        )

      },

      change_instance_from_id: function (id: number) {
        if (!this.instance_list || this.instance_list.length == 0) {
          return
        }
        this.desired_instance_index = this.instance_list.findIndex(instance => {
          return instance.id == id
        })
        this.change_instance_from_index(this.desired_instance_index)
      },

      change_instance_from_index: function (index: number) {
        this.change_instance(this.instance_list[index], index)
      },

      change_instance: function (instance, index) {

        if (!instance) {
          instance = {}
        }  // to avoid having as many exists/ doesn't exist checks elsewhere

        this.current_instance = instance
        this.current_instance_index = index

        let instance_id = null  // so it clears if no valid ID yet... not sure if this is a good idea
        if (instance && instance.id) {
          instance_id = instance.id
        }
        if (instance_id != null) {
          // this.$addQueriesToLocation({'instance': instance_id})
          // this.$route.query.instance = instance_id
        }
      },

      show_all: function () {
        if (this.focus_mode == false) {
          return
        }
        this.$emit('show_all')
        this.focus_mode = false
        this.instance_focused_index = null
      },
      focus_model_run: function (model_run) {
        // Reset Hidden
        this.instance_list.forEach(inst => {
          inst.hidden = false;
        })
        if (this.current_model_run_filter && (this.current_model_run_filter.id === model_run.id)) {
          this.current_model_run_filter = null;
          this.$emit('update_canvas');
          return
        }
        // Set new filter
        this.instance_list.forEach(inst => {
          if (inst.model_run_id === model_run.id && model_run.id !== -1) {
            inst.hidden = false
          } else if (model_run.id === -1 && !inst.model_run_id) {
            inst.hidden = false;
          } else {
            inst.hidden = true;
          }
        })
        this.current_model_run_filter = model_run;
        this.$emit('update_canvas');
      },
      toggle_instance_focus: function (
        instance_index: number,
        instance_id) {

        this.focus_mode = true

        this.change_instance_from_index(instance_index)

        // maybe passing render mode here is stronger than list type?
        this.$emit('toggle_instance_focus',
          {
            'index': instance_index,
            'render_mode': this.render_mode
          })
        this.instance_focused_index = instance_index
      },

      instance_update: function (
        mode,
        instance_index,
        instance_id,
        list_type = 'default',
        payload = null) {

        this.$emit('instance_update', {
          'mode': mode,
          'payload': payload,
          'index': instance_index,
          'id': instance_id,
          'list_type': list_type
        })
      },
      get_instance_color(instance) {
        if (instance.override_color) {
          return this.style_color(instance.override_color)
        } else {
          return this.style_color(this.label_file_colour_map[instance.label_file_id].hex)
        }
      },
      style_color: function (hex) {
        return "color:" + hex
      },
      style_instance_selected_color: function (item) {
        let color = this.$vuetify.theme.themes.light.primary
        if (item == this.current_instance) {
          color = this.$vuetify.theme.themes.light.secondary
        }
        return 'cursor: pointer; color:' + color
      }

    }
  }
) </script>

<style scoped>
.color-box:hover {
  cursor: pointer;
}

.sidebar-accordeon-header {
  border-bottom: 1px solid #e0e0e0;
}
</style>
<style>

.v-expansion-panel-content__wrap {
  padding: 0 !important;
}
</style>
