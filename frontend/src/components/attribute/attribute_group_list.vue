<template>
<div id="">

<v-progress-linear class="mt-4" indeterminate v-if="loading"></v-progress-linear>
<div style="overflow-y:auto">
  <v-layout v-if="mode == 'edit' " class="d-flex pa-4 align-center">

    <!-- TODO trying to separate out this from the list layout
      since we have different goals for annotation vs
      admin thing here...-->

    <attribute_group_new
        :schema_id="schema_id"
        :project_string_id="project_string_id">

    </attribute_group_new>

    <v-btn color="primary"
           text
           href="https://diffgram.readme.io/docs/attributes-1"
           target="_blank"
           icon>
      <v-icon>help</v-icon>
    </v-btn>


  </v-layout>

  <!--  Caution     This is for  annotate mode too -->
  <v-layout column v-if="mode == 'edit'
            || current_instance
            && current_instance.soft_delete != true">

    <v_error_multiple :error="error">
    </v_error_multiple>


    <!-- TODO use tree syntax from vue js -->
    <v-expansion-panels
       v-model="openedPanel"
      :accordion="true"
      :popout="false"
      :inset="false"
      :multiple="false"
      :focusable="true"
      :disabled="false"
      :flat="false"
      :hover="false"
      :tile="true"

    >
      <v-expansion-panel
        v-for="group in attribute_group_list_computed"
        :key="group.id"
      >
        <v-expansion-panel-header
                        style="border: 1px solid #e0e0e0"
                        :data-cy="`attribute_group_header_${group.prompt}`"
                        @click="update_url_with_current_group(group)"
                        class="d-flex justify-start text-left">
          <h4 class="text-left d-flex align-center flex-grow-1">
            <attribute_kind_icons
              class="pr-2"
              :kind=" group.kind "
            >
            </attribute_kind_icons>

            {{group.prompt}}

            <div v-if="!group.prompt"
                 :data-cy="`attribute_group_header_Untitled Attribute Group`">
              Untitled Attribute Group
            </div>

            <v-spacer></v-spacer>
            <!-- Archive button -->
            <button_with_confirm
              v-if="mode === 'edit'"
              @confirm_click="api_group_archive(group)"
              icon="archive"
              color="red"
              :loading="loading"
              :disabled="loading"
              :icon_style="true"
              tooltip_message="Archive Entire Attribute and All Options"
            >
              <template slot="content">
                <v-layout column>

                  <v-alert type="error">
                    Are you sure? This will remove all options too.
                  </v-alert>

                </v-layout>
              </template>
            </button_with_confirm>
          </h4>
          <!-- Archive button -->
          <!-- TODO maybe, play with this more
            eg maybe in edit mode show internal tag-->

        </v-expansion-panel-header>

        <v-expansion-panel-content>
          <attribute_group
            :schema_id="schema_id"
            :project_string_id="project_string_id"
            :mode="mode"
            :view_only_mode="view_only_mode"
            :group="group"
            :key="group.id"
            @attribute_change="$emit('attribute_change', $event)"
            :current_instance="current_instance"
          >
          </attribute_group>

          <div v-if="mode == 'edit'">
            ID: {{group.id}}
          </div>
        </v-expansion-panel-content>

      </v-expansion-panel>

    </v-expansion-panels>


  </v-layout>


</div>

</div>
</template>

<script lang="ts">


import axios from '../../services/customInstance';
import draggable from 'vuedraggable'

import attribute_group from './attribute_group.vue';
import {attribute_group_list} from '../../services/attributesService';
import attribute_kind_icons from './attribute_kind_icons.vue';
import attribute_group_new from './attribute_group_new.vue'


 import Vue from "vue"; export default Vue.extend( {

   // TODO may want to rename now that seeing
   // dependency between knowing which parent / "were" we are creaing a new
   // action and parent.

    name: 'attribute_group_list',

    components: {
      draggable: draggable,
      attribute_group: attribute_group,
      attribute_kind_icons: attribute_kind_icons,
      attribute_group_new: attribute_group_new

    },

    props: {

      'project_string_id' : {
        default: null
      },
      'schema_id':{
        required: true
      },

      // edit, annotate,  ...
      'mode' : {
        default: null
      },

      'attribute_group_list_prop' : {
        default: null
      },

      'current_instance' : {
        default: null
      },

      'view_only_mode' : {
        default: false
      }


    },

    data() {
      return {

        loading: false,
        error: {},
        success: false,

        name: null,
        attribute_group_list: [],
        out_of_schema_attributes: [],

        openedPanel: null

      }
    },

    watch: {
      schema_id: function(new_val, old_val){
        this.api_attribute_group_list("from_project")
      },
      attribute_template_group_id(new_val, old_val) {
        this.api_attribute_group_list("from_project")
      },

      attribute_group_list_prop() {
        this.attribute_group_list = this.attribute_group_list_prop
      },
      current_instance(){
        this.fetch_current_instance_missing_attributes("from_project")
      }

    },

    created() {
      // is edit right name? or "from_project" as seperate context / mode here too
      if (this.mode == 'edit') {
       this.api_attribute_group_list("from_project")
      }

      if (this.mode == 'annotate') {
       this.attribute_group_list = this.attribute_group_list_prop
        this.fetch_current_instance_missing_attributes("from_project")
      }

    },
    mounted() {

      // ie triggered by  this.$store.commit('attribute_refresh_group_list')
      // defined in store.js action
      var self = this
      this.refresh_watcher = this.$store.watch((state) => {
        return this.$store.state.attribute.refresh_group_list
      },
        (new_val, old_val) => {
          self.api_attribute_group_list("from_project")
        },
      )

      if (this.$route.query.attribute_group) {
        this.open_panel_by_id(this.$route.query.attribute_group)
      }

    },
    destroyed() {
      this.refresh_watcher() // destroy
    },
    computed: {
      attribute_group_list_computed: function(){
        if(!this.current_instance){
          return this.attribute_group_list
        }
        let all_attributes = this.attribute_group_list.concat(this.out_of_schema_attributes);
        let result = [];
        for(let attr of all_attributes){
          let id_list = attr.label_file_list.map(elm => elm.id);
          if(id_list.includes(this.current_instance.label_file_id)){
            result.push(attr)
          }
        }
        return result
      }
    },
    methods: {
      api_group_archive: async function (group) {
        this.loading = true
        this.error = {}
        this.success = false
        try{
          const response = await axios.post(
            '/api/v1/project/' + this.project_string_id +
            '/attribute/group/update',
            {
              group_id: Number(group.id),
              mode: 'ARCHIVE',
              kind: group.kind,

            })
          this.success = true
          this.loading = false
          this.$store.commit('attribute_refresh_group_list')
        }
        catch(error) {
          if (error) {
            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            console.error(error)
          }
        }
      },
      open_panel_by_id(id: number){
        if (!this.attribute_group_list) {return }
        this.openedPanel = this.attribute_group_list.findIndex(x => {
          return x.id == id
        })
      },

      update_url_with_current_group(group) {
        this.$addQueriesToLocation({'attribute_group': group.id})
      },
      fetch_current_instance_missing_attributes: async function(mode){
        /*
        * Fetches any attributes that are not on the current schema. This is useful when a user
        * changed the schema of a task template and it already had attributes from prev schema.
        * */

        if(!this.current_instance){
          return
        }
        let attr_dict = this.current_instance.attribute_groups;
        if(!attr_dict){
          return
        }
        let attribute_group_id_list = Object.keys(attr_dict).map(elm => parseInt(elm, 10));
        let existing_attribute_id_list = this.attribute_group_list.map(elm => elm.id);
        let missing_id_list = [];
        for (let id of attribute_group_id_list){
          if(!existing_attribute_id_list.includes(id)){
            missing_id_list.push(id)
          }
        }
        if(missing_id_list.length === 0){
          return
        }
        let [attr_data, error] = await attribute_group_list(
          this.project_string_id,
          undefined,
          undefined,
          mode,
          missing_id_list,
          true
        )

        if(error){
          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
          this.error = this.$route_api_errors(error)
          this.loading = false
          return
        }
        if(attr_data){
          let attribute_group_list = attr_data.attribute_group_list
          this.out_of_schema_attributes = attribute_group_list

        }

      },
      api_attribute_group_list: async function (mode) {

        this.loading = true
        this.error = {}
        this.success = false
        let [attr_data, error] = await attribute_group_list(
          this.project_string_id,
          this.attribute_template_group_id,
          this.schema_id,
          mode,
          true
        )
        if(error){
          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
          this.error = this.$route_api_errors(error)
          this.loading = false
          return
        }
        if(attr_data){
          let attribute_group_list = attr_data.attribute_group_list
          this.attribute_group_list = attribute_group_list.sort(
            (a, b) => b.id - a.id);
          await this.fetch_current_instance_missing_attributes(mode)
          this.success = true
          this.loading = false

        }
      }


    }
  }
) </script>
