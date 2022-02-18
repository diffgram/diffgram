<template>
  <div v-cloak class="d-flex align-center justify-start" >
    <v-progress-circular indeterminate class="mr-4" color="primary" v-if="label_refresh_loading"></v-progress-circular>
    <v-layout >

      <v-select :items="label_list_with_limit"
                style="min-height: 55px"
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


          <!-- hacky word around because
              when we use the custom template select thing
              it seems to get confused on highlight colors

              The assumption is that it should still do the highlighting
              properly, but I guess because we are controling it doesn't

              I can't seem to find a good reference for what property
              is setting if each item is selected or not.
              (ie I would expect a state of item.selected == true or something)
              perhaps they are doing this when the default selection thing is there
              OR it's just a bug? either way leaving it for now, maybe
              something can do a ticket about later but already spent waay
              too much time here.

              -->
          <v-chip v-if="is_selected(data.item)"
                  class="pa-0"
                  color="white"
                  text-color="secondary">
            {{data.item.label.name}}
          </v-chip>
          <v-chip v-else
                  class="pa-0"
                  color="white"
                  text-color="primary">
            {{data.item.label.name}}
          </v-chip>

        </template>

        <template v-slot:selection="data">

          <!-- Not sure if fan of "chip" thing,
              but  either way want to not have the "left" thing for
              icon I think here-->

          <span color="white" >
            <v-icon
              :style="style_color(data.item.colour.hex)">
              flag
            </v-icon>

            <v-icon v-if="data.item.label.default_sequences_to_single_frame"
                    color="black">
              mdi-flag-checkered
            </v-icon>

            {{ data.item.label.name}}
          </span>

        </template>


      </v-select>

      <tooltip_icon
        class="pa-4"
        tooltip_message="+ More Schema"
        v-if="over_limit"
        icon="mdi-more">
      </tooltip_icon>

      <!-- Select all -->

      <!-- TODO consider this for layout
         https://codepen.io/aaaaaaaaaaaaaaaaaaa/pen/wvaoeRj?editors=1010

          Downside is it actually requires an extra click
        -->
      <div v-if="multiple == true
       && !view_only_mode
       && show_select_all == true">
        <v-checkbox
          data-cy="select-all-labels"
          v-model="select_all_state"
          label="Select All"
          :disabled="label_refresh_loading"
          @change="select_all_toggle"
        >
        </v-checkbox>
      </div>

    </v-layout>

  </div>
</template>

<script lang="ts">

  import axios from '../../services/customInstance';

  import Vue from "vue";

  export default Vue.extend({

      name: 'label_select_only',

      props: {
        'project_string_id': {},
        // note we currently use project
        // from store, ie for case of job/new
        // where in project scope but want to see labels still
        'mode': {
          default: null,
          type: String
          // 'multiple' is an option STRING
        },
        'view_only_mode': {},
        'datacy': {
          default: 'label_select_only',
          type: String
        },
        'attribute_group_id': {},

        'load_selected_id_list': {
          type: Array
        },
        // IDs NOT objects.
        // ie :load_selected_id_list="job.label_dict.label_file_list"
        // TODO would be a good typescript thing to enforce
        // ie Array<Number>... but that exact syntax doesn't quite work

        'select_all_at_load': {
          default: false
          // select_all_at_load only fires if load_selected_id_list
          // is null
        },
        'select_this_id_at_load': {
          default: null
        },
        /* The default assumption with this component is that
          * we are getting labels from a project to work with
          * If we provide a label file list directly, ie from a job
          * Then assumption is we just want to render it?
          * Or at the very least that we don't want to / can't
          * get it from project scope
          */
        'label_file_list_prop': {},

        'request_refresh_from_project': {
          default: null
        },
        'show_select_all': {
          default: true
        },
        'label_prompt': {
          default: 'Label'
        },
        'limit': {
          default: null
        }
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
          // this.emit_selected() // in case something relies on this,
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
        set_label_list: function(label_list){
          this.label_list = label_list;
        },
        check_select_all_state: function () {
          /* Just do length check,
           * Doing this doesn't work: $vm0.label_list == $vm0.selected
           *  https://stackoverflow.com/questions/3115982/how-to-check-if-two-arrays-are-equal-with-javascript
           *
           * Note this is JUST for UI benefit, we do check again for changing it
           *
           */
          if (this.selected.length === this.label_list.length) {
            this.select_all_state = true
          } else {
            this.select_all_state = false
          }
        },
        select_all_toggle: function () {
          /*
           * Vuetify has some built in stuff but does not appear to for this type
           * of a selector and either way we have other things here that effect
           * the state and detection of it. Seems like OK way to do this. Also found
           * this after https://codepen.io/aaaaaaaaaaaaaaaaaaa/pen/wvaoeRj?editors=1010
           *
           * Manual test cases
           *
           * 1) Load known thing, expect check state to work
           * 2) Try "Clearing" it, expect it to clear
           * 3) Try select all, expect all to be selected
           * 4) Deselect a single one, expect select all to be deselected
           *
           * Key is that we emit selected here after to push update to server
           */
          if (this.selected.length === this.label_list.length) {
            this.selected = []
          } else {
            this.selected = this.label_list.slice()
          }
          this.emit_selected()
        },

        is_selected: function (item) {
          if (this.multiple == true &&
            this.selected && this.selected.includes(item)) {
            return true
          }
          return false
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
              console.error(error);
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
          // ie if we unselect a single one
          // then need to update state.
          this.check_select_all_state()

          // TODO think about naming this @change / 'change'
          // to better align with other stuff
          this.$emit('selected_ids_only', this.selected_ids_only)
          this.$emit('label_file', this.selected)
        }

      }
    }
  ) </script>
