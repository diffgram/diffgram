<template>
  <div id="">

    <!-- 
      note for formatting we keep the "annotation" display separate
      from the "administration" thing, different formatting goals
      ie tight space conservation vs seperation for different groups.

      For context in earlier versions this was even more confusing because
      the prompt was part of a seperate group so was hard to tell what was
      changing

      now 2 seperate modes... much more clear.
      -->

    <v-card
        v-if="mode === 'annotate' "
        elevation="0">

      <v-container>

        <!-- Minimal padding here to free up screen real estate-->
        <v-layout>

          <!--  for veutify 2 moved the event @change to the group
            as didn't seem to be working as expected on v-radio  (event payload was undefined)
            found out after it not setting it MAY have been unrelated
            something to review later-->

          <!-- 
              v-model here returns an object  -->

          <v-radio-group
            class="pa-0"
            :data-cy="`${group.prompt}_value_radio_buttons`"
            :label="group.prompt"
            @change="attribute_change()"
            v-model="internal_selected"
            v-if="group.kind == 'radio'"
          >
            <v-radio
              :data-cy="`${group.prompt}_radio_${item.display_name}`"
              :disabled="view_only_mode"
              v-for="item in select_format"
              :key="item.name"
              :label="`${item.display_name}`"
              :value="item"
            ></v-radio>
          </v-radio-group>


          <!-- FUTURE here we would declare if it
             pulls up a NESTED group or something
             otherwise assume it's the "value" being returned
             (kind is set at group level) -->

          <!--
              Text field limit to 1 for now, too many complications with allowing many here...
              Would probably want to abstract a "multiple textfield"
              into something else if we allowed this...
            -->

          <v-text-field
            v-if="group.kind == 'text'"
            :data-cy="`${group.prompt}_value_textfield`"
            v-model="internal_selected"
            :label="group.prompt"
            :disabled="loading || view_only_mode"
            @change="attribute_change"
            @keyup="attribute_change"
            @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
            @blur="$store.commit('set_user_is_typing_or_menu_open', false)"

          >
          </v-text-field>


          <diffgram_select
            v-if="group.kind == 'multiple_select'"
            :data_cy="`${group.prompt}_value_multiple_select`"
            :item_list="select_format"
            :multiple="true"
            :return_object="true"
            v-model="internal_selected"
            :label="group.prompt"
            :disabled="loading || view_only_mode"
            @change="attribute_change()"
          >
          </diffgram_select>

          <!-- Single select

            return_object true becasue we want to be able to switch between
            the radio and select without hurting data

            Default if no kind (for migration)
            -->
          <diffgram_select
            v-if="group.kind == 'select' || !group.kind"
            :data_cy="`${group.prompt}_value_select`"
            :item_list="select_format"
            :return_object="true"
            :multiple="false"
            v-model="internal_selected"
            :label="group.prompt"
            :disabled="loading || view_only_mode"
            @change="attribute_change()"
          >
          </diffgram_select>

          <v-container class="d-flex align-content-center justify-start"  v-if="group.kind === 'slider' || !group.kind">
            <v-slider
              :data-cy="`${group.prompt}_value_slider`"
              :min="group.min_value"
              :max="group.max_value"
              v-model="internal_selected"
              :label="group.prompt"
              :disabled="loading || view_only_mode"
              @change="attribute_change()"
            >
            </v-slider>
            <p>{{internal_selected}}</p>
          </v-container>

          <v-time-picker
            v-if="group.kind === 'time' || !group.kind"
            v-model="internal_selected"
            :label="group.prompt"
            full-width
            :disabled="loading || view_only_mode"
            @change="attribute_change()"
            @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
            @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
            clearable
          >

          </v-time-picker>

          <v-date-picker
            v-if="group.kind === 'date' || !group.kind"
            v-model="internal_selected"
            :label="group.prompt"
            :disabled="loading || view_only_mode"
            @change="attribute_change()"
            @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
            @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
            clearable
          >
          </v-date-picker>
        </v-layout>

      </v-container>
    </v-card>


    <!-- EDIT  -->

    <v-container v-if="mode == 'edit' ">
      <v-container class="pa-8">

        <v-row class="d-flex align-center">
          <v-col cols="3">
            <!-- KIND -->
            <diffgram_select
              data_cy="attribute_kind_select"
              :item_list="kind_list"
              v-model="group.kind"
              label="Kind"
              :disabled="loading || !kind_warning_monitor(group.kind)"
              @change="api_group_update('UPDATE')"
            >
            </diffgram_select>
          </v-col>
          <v-col cols="4">
            <v-text-field label="Prompt Shown"
                          data-cy="attribute_prompt"
                          v-model="group.prompt"
                          @change="api_group_update('UPDATE')"
            >
            </v-text-field>
          </v-col>
          <v-col cols="2">
            <v-text-field label="Internal Tag"
                          data-cy="attribute_tag"
                          v-model="group.name"
                          @change="api_group_update('UPDATE')"
            >
            </v-text-field>
          </v-col>
          <v-col cols="1">


            <!-- Label -->


            <!--
            <v-alert type="info" v-if="group.kind == 'text'">

            </v-alert>
            -->

            <!-- "Edit" in this context is not about editing the
              attribute, but the administration process of creating
              attributes vs actually annotating them
              TODO adjust wording to make this more clear in code

              Text case
               * Don't snow "new" for text because we only allow one,
              and the group level prompt is used as the label.

               For now still show the list of attributes ie if a user
              wants to change it back.
              -->

            <button_with_menu
              tooltip_message="New Attribute"
              data-cy="new_attribute_option_button"
              datacyclose="close_button_new_attribute"
              v-if="group && group.kind != 'text' && group.kind != 'slider' "
              icon="add"
              :large="true"
              color="green"
              :close_by_button="true"
            >
              <template slot="content">

                <attribute_new_or_update
                  :project_string_id="project_string_id"
                  :group_id="group.id"
                >

                </attribute_new_or_update>

              </template>

            </button_with_menu>

          </v-col>
          <v-col col="1">
            <!-- Archive button -->
            <button_with_confirm
              @confirm_click="api_group_update('ARCHIVE')"
              class="text-right pa-4"
              icon="archive"
              color="red"
              :loading="loading"
              :disabled="loading"
              :icon_style="true"
              tooltip_message="Archive"
            >
            </button_with_confirm>
            <!-- Archive button -->

          </v-col>


        </v-row>
        <v-row v-if="group.kind === 'slider'">
          <v-col cols="3">
            <v-text-field v-model="group.min_value"
                          @change="api_group_update('UPDATE')"
                          type="number"
                          data-cy="min_value"
                          label="Min Value">

            </v-text-field>
          </v-col>
          <v-col cols="3">
            <v-text-field v-model="group.max_value"
                          @change="api_group_update('UPDATE')"
                          type="number"
                          data-cy="max_value"
                          label="Max Value">

            </v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <label_select_only
              datacy="label_select_attribute"
              :project_string_id="project_string_id"
              :mode=" 'multiple' "
              :attribute_group_id="group.id"
              @label_file="recieve_label_file($event)"
            >
            </label_select_only>
          </v-col>

        </v-row>

        <!-- Edit Default  default_id default_value -->
        <v-row>
          <v-col cols="12">

            <v-text-field
              v-if="group.kind == 'text'"
              v-model="group.default_value"
              label="Default"
              :disabled="loading || view_only_mode"
              @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
              @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
              @change="api_group_update('UPDATE')"
              clearable

            >
            </v-text-field>

            <diffgram_select
              v-if="['select', 'multiple_select', 'radio'].includes(group.kind)"
              :item_list="select_format"
              v-model="group.default_id"
              label="Default"
              :disabled="loading || view_only_mode"
              @change="api_group_update('UPDATE')"
              :clearable="true"
            >
            </diffgram_select>

            <v-text-field
              v-if="group.kind === 'slider'"
              type="number"
              v-model="group.default_value"
              label="Default"
              :disabled="loading || view_only_mode"
              @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
              @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
              @change="api_group_update('UPDATE')"
              clearable

            >
            </v-text-field>
            <v-container v-if="group.kind === 'time'">
              <p><strong>Default: </strong></p>
              <p v-if="!group.default_value"> (None Yet)</p>
              <v-time-picker
                v-model="group.default_value"
                label="Default"
                :disabled="loading || view_only_mode"
                @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                @change="api_group_update('UPDATE')"
                clearable
              >
              </v-time-picker>
            </v-container>

            <div v-if="group.kind === 'date'">
            <p><strong>Default: </strong></p>
            <p v-if="!group.default_value"> (None Yet)</p>
            <v-date-picker
              v-model="group.default_value"
              label="Default"
              :disabled="loading || view_only_mode"
              @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
              @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
              @change="api_group_update('UPDATE')"
              clearable
            >
            </v-date-picker>
            </div>
          </v-col>
        </v-row>


        <v-layout>

          <v_error_multiple :error="error">
          </v_error_multiple>

          <v-container container--fluid grid-list-md>

            <draggable
              v-if="group"
              v-model="group.attribute_template_list"
              draggable=false
            >

              <template
                v-for="item in group.attribute_template_list">

                <attribute
                  :project_string_id="project_string_id"
                  :attribute="item"
                  :key="item.id"
                >
                </attribute>

              </template>

            </draggable>


          </v-container>


        </v-layout>


      </v-container>

      <!-- On bottom so it doesn't bounce screen when fires -->
      <v-alert v-if="success" type="success" dismissible>Attribute updated successfully.</v-alert>

    </v-container>

  </div>
</template>

<script lang="ts">
  // @ts-nocheck

  import axios from 'axios';
  import draggable from 'vuedraggable'
  import attribute from './attribute.vue';
  import attribute_new_or_update from './attribute_new_or_update.vue';
  import label_select_only from '../label/label_select_only.vue'
  import attribute_kind_icons from './attribute_kind_icons';


  import Vue from "vue";

  export default Vue.extend({

      name: 'attribute_group',

      components: {
        draggable,
        attribute,
        attribute_new_or_update,
        label_select_only,
        attribute_kind_icons

      },

      props: {

        'project_string_id': {
          default: null
        },
        'group': {
          default: {}
        },
        // edit, annotate,  ...
        'mode': {
          default: null
        },

        'current_instance': {
          default: null
        },

        'view_only_mode': {
          default: false
        }

      },

      data() {
        return {

          first_load: true,
          original_kind: null,
          min_value: 1,
          max_value: 10,

          loading: false,
          error: {},
          success: false,

          internal_selected: null,

          kind_list: [

            {
              'display_name': 'Select',
              'name': 'select',
              'icon': 'mdi-selection',
              'color': 'primary'
            },
            {
              'display_name': 'Free Text',
              'name': 'text',
              'icon': 'mdi-card-text',
              'color': 'green'
            },
            {
              'display_name': 'Multiple Select',
              'name': 'multiple_select',
              'icon': 'mdi-select-multiple',
              'color': 'purple'
            },
            {
              'display_name': 'Radio Buttons',
              'name': 'radio',
              'icon': 'mdi-radiobox-marked',
              'color': 'pink'
            },
            {
              'display_name': 'Slider',
              'name': 'slider',
              'icon': 'mdi-video-input-component',
              'color': 'pink'
            },
            {
              'display_name': 'Time',
              'name': 'time',
              'icon': 'mdi-clock',
              'color': 'primary'
            },
            {
              'display_name': 'Date',
              'name': 'date',
              'icon': 'mdi-calendar',
              'color': 'primary'
            }

            // future
            /*
            {
              'display_name': 'Open nested selection to new group',
              'name': 'chidren',
              'icon': 'mdi-function-variant'
            }
            */

          ],

          name: null,

          label_file_list: []

        }
      },

      watch: {

        // not sure if this is right thing to watch
        current_instance() {
          this.set_existing_selected()
        },

        group() {
          // for "resesting" it.
          // we want a newly created group to be different
          // vue js being a bit fiddly here
          this.original_kind = this.group.kind
        }

      },

      created() {

        this.set_existing_selected()

        this.original_kind = this.group.kind

      },
      mounted() {


      },
      destroyed() {

      },
      computed: {

        select_format: function () {
          /* Convert a list of data base objects into form
           * diffgram_select wants
           *
           * also helps keep format we save it in uniform
           * in case a user switches between selector types
           *
           * and/or we change what we are sending from backend later
           */

          if (this.group.kind == "text") {
            return
          }

          let attribute_template_list = []

          /*
           * Another option is we could just add
           * The display name and name to the existing object
           * advantage is if we do want to reduce what we store
           * here we can do that
           */

          for (let x of this.group.attribute_template_list) {

            let attribute = {}
            attribute.display_name = x.name
            attribute.id = x.id
            attribute.name = x.id   // temp duplication thing, diffgram_select expects a name

            attribute_template_list.push(attribute)
          }

          return attribute_template_list

        }
      },
      methods: {

        // group change
        attribute_change: function () {

          /*
           *
           * the theory here is mainly that it is maintaining the same format
           * so we are always setting a
           *
           * group_id :  actual group data

            Attribute group is responsible for loading it’s group of attributes,
            including existing data from a given Instance

            It emits an event that contains the group id, and the new “value”
            value could be one of [string, object, list, node (future)]

            Node could potentially be another group in the future

            Annotation core is responsible for saving a dict where the key
            is the group id and the value for that instance.

            More: https://docs.google.com/document/d/1bkq8ftciLqDtlmFRrm-dJmPGmIV5Cra8YnegSTXJJbc/edit#heading=h.51y9ufvnioeu

           *
           */
          this.$emit('attribute_change', [this.group, this.internal_selected])

        },

        get_default: function () {
          if (this.group.default_id){
            return this.group.default_id
          }
          if (this.group.default_value){
            return this.group.default_value
          }
        },

        format_default: function () {

          if ([null, "select", "radio"].includes(this.group.kind)) {
            let default_attribute = {}
            default_attribute.id = this.group.default_id
            return default_attribute
          }
          if (this.group.kind == 'multiple_select'){
            return [this.group.default_id]  // note array formatting, assumed to be single ID for now
          }
          if (this.group.kind == 'text'){
            return this.group.default_value
          }
          if(this.group.kind === 'slider'){
            return this.group.default_value;
          }
          if(this.group.kind === 'time'){
            return this.group.default_value;
          }
          if(this.group.kind === 'date'){
            return this.group.default_value;
          }

        },

        set_existing_selected: function () {
          /* 
           * In context of annotation this component is focused
           * on displaying attributes and propogating selections
           * If an instance already has selections then we need to set it,
           * and since vue js seems to like component reuse (I think this was reason)
           * we need to reset it if the current_instance changes
           *
           * We are already in the context of a specific group
           * so here we are looking at the dict of groups in the current
           * instance and seeing if any
           * match the group id (this avoids a n^2 setup?)
           *
           * This was really more for the "single select" otherwise can just load from instance right?
           *
           */

          // reset
          this.internal_selected = null

          // set existing if applicable
          if (!this.current_instance) {
            return
          }

          // note this is basing off the current instance!

          /*
           * TYPES: Different types treated differently
           *
           *  the values for attribute groups are diverse
           *  effectively we assume that whatever format it stores the value in is what we will
           *  reload it as
           *
           *  we can't just use ids because of free text fields (like 137 in this example)
           *
           *  and the form of the data changes since some things prefer to store in arrays
           *  some as objects and some as straight ids...
           *
           *  the form is determined by the group type
           *  and then by the front end select controls here
           *
           *  the backend stores whatever it is given for these things
           *
           *  EXAMPLE:
             *    136: Object
                  137: "dog"
                  138: Array[3]
                  139: 180
                  // future maybe a Node
           */

          /*
           * Prior we iterated through the whole list but that doesn't really make sense
           * because we only care about the group id
           *
           * IMPORTANT - instance group value != current group
           *
           *    this is the current instance data which is different from
           *    the current group
           *
           *    for example the current group may be "apple"
           *    but there may be no selection for "apple" yet on the specific instance.
           *
           */

          let value = null    // shared with existing and default
          let existing_value = null
          let default_value = null

          if (this.current_instance.attribute_groups) {
            existing_value = this.current_instance.attribute_groups[this.group.id]
          }
          if (existing_value != null){
            value = existing_value
          }

          else  {
            // If not existing value, check for default
            // We must be careful here, we don't want to "reset" to the default value
            // if there was an existing value. We only set default when it's null.
            default_value = this.get_default()
            if (!default_value) {
              // If no default and no exist_value to set so return
              return
            } else {
              value = this.format_default()
            }
          }

          // Code below is for LOADING VALUES / formatting.
          // At this point we around know the value itself as ( existing_value )

          // We use id because the attributes may have been updated since they were selected

          /*  Radio buttons have bug in veutify that requires object selection
           *  BUT that's a primary reason, main thing is because we want to use
           *  IDs incase the "text" for the id changes
           */

          /* Caution we want to use "this.group" thing here since existing_value
           * will NOT have the kind (it ONLY has instance specific information)
           */

          if (!this.group.kind || this.group.kind == "select" || this.group.kind == "radio") {
            this.internal_selected = this.select_format.find(
              attribute => {
                return attribute.id == value.id
              })

          } else if (this.group.kind == "text") {
            // in this case nothing to change we are only storing text
            this.internal_selected = value

          } else if (this.group.kind == "multiple_select") {

            this.internal_selected = []
            // value is an array now
            for (let single_selected of value) {
              this.internal_selected.push(this.select_format.find(
                attribute => {
                  return attribute.id == single_selected.id
                }))
            }

          }
          else if(this.group.kind === 'slider'){
            if(!this.group.min_value){
              this.group.min_value = 1;
            }
            if(!this.group.max_value){
              this.group.max_value = 10;
            }
            this.internal_selected = parseInt(value, 10)
          }
          else if(this.group.kind === 'time'){
            this.internal_selected = value
          }
          else if(this.group.kind === 'date'){
            this.internal_selected = value
          }

          if (default_value) {
            // IF we added a default value, emit the change
            // The above setting is done automatically (not by user)
            // eg if it's existing, then there's no need to emit change
            this.attribute_change()
          }


        },


        kind_warning_monitor: function (value) {
          /* When a group is first created it can have a blank kind
           * So we want user to edit this freely
           * Then once it's set we warn
           *
           * In future could also do a hard restriction here...
           *
           * Allow swap between radio and select?
           *
           * Because we don't update original kind, the person
           *  can flip freely through newly created groups
           *  and this should only display if they come back to the page.
           *
           *  Consider:
           *  We also check that there must be at least one attribute
           *  or other things so it doesn't show up for new users
           *  (this wouldn't work for "text" type though)
           *
           *  Enforcing this
           *    We would need to run this first
           *    then run / not run the update request
           *    otherwise timing issue because it does the API call even
           *    if the group is set...
           *
           *    Also not really wanting to have such a hard "enforcement" here?
           *    Flip side is right now front end can look broken since it will show
           *    object...
           *
           *
           *  manual test case
           *    -> Reloading page I expect it to be locked (as long as labels present)
           *    -> New group I expect it to be availabe
           *    -> new group with labels (haven't gone off page) I still expect it to be available
           *
           *   At the moment if we remove labels it becomes available again...
           *    but I think that's something we can address later...
           */

          /* This allowed swap list was in a different context,
           * it was more of a "validation" rule, ie that
           * runs when it changes. Realized for now the bigger concern is more
           * disabling it in the first place.
           */

          /*
          let allowed_swap_list = ["select", "radio"]

          if (allowed_swap_list.includes(this.original_kind)
            && allowed_swap_list.includes(value)) {
            return true
          }
          */

          if (!this.original_kind) {
            return true
          }

          // we assume if no labels selected it's ok
          if (this.label_file_list.length == 0) {
            return true
          }

          // default case if other things aren't true
          return false

        },

        recieve_label_file: function (label_file_list) {


          this.label_file_list = label_file_list

          // this feels a bit hacky but at least should work for now...
          if (this.first_load == true) {
            this.first_load = false
          } else {

            this.api_group_update("UPDATE")
          }


        },


        api_group_update: function (mode) {
          this.loading = true
          this.error = {}
          this.success = false

          if (mode == 'ARCHIVE') {
            // backend validates that a kind exists
            // so doing this as a work around
            this.group.kind = "ARCHIVE"
          }
          let min_value, max_value;
          if(this.group.kind === 'slider'){
            min_value = parseInt(this.min_value, 10);
            max_value = parseInt(this.max_value, 10);
            if(max_value < parseInt(this.group.default_value, 10)){
              max_value = parseInt(this.group.default_value, 10)
              this.group.max_value = max_value;
            }
            if(min_value > parseInt(this.group.default_value, 10)){
              min_value = parseInt(this.group.default_value, 10)
              this.group.min_value = min_value;
            }
          }
          axios.post(
            '/api/v1/project/' + this.project_string_id +
            '/attribute/group/update',
            {
              group_id: Number(this.group.id),
              name: this.group.name,
              prompt: this.group.prompt,
              label_file_list: this.label_file_list,
              kind: this.group.kind,
              default_id: this.group.default_id,
              default_value: this.group.default_value,
              min_value: min_value,
              max_value: max_value,
              mode: mode

            }).then(response => {

            //this.group = response.data.group

            this.success = true
            this.loading = false

            // response.data.log.info


            // careful mode is local, not this.mode
            if (mode == 'ARCHIVE') {

              // only refresh on archive?

              this.$store.commit('attribute_refresh_group_list')
            }
            if(this.group.kind === 'slider'){
              if(!this.group.min_value){
                this.group.min_value = 1;
              }
              if(!this.group.max_value){
                this.group.max_value = 10;
              }
            }

          }).catch(error => {

            if (error) {
              if (error.response.status == 400) {
                this.error = error.response.data.log.error
              }
              this.loading = false
              console.log(error)
            }
          });

        }

      }
    }
  ) </script>
