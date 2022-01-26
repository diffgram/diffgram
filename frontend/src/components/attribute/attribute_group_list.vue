<template>
<div id="">

<div style="overflow-y:auto">
  <v-layout v-if="mode == 'edit' " class="pa-8">

    <!-- TODO trying to separate out this from the list layout
      since we have different goals for annotation vs
      admin thing here...-->

    <attribute_group_new
        :project_string_id="project_string_id">

    </attribute_group_new>

    <v-spacer></v-spacer>

    <tooltip_button
        tooltip_message="Attribute Help"
        href="https://diffgram.readme.io/docs/attributes-1"
        icon="mdi-lifebuoy"
        :icon_style="true"
        :large="true"
        color="red">
    </tooltip_button>


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
        v-for="group in attribute_group_list"
        :key="group.id"
      >
        <v-expansion-panel-header
                        style="border: 1px solid #e0e0e0"
                        :data-cy="`attribute_group_header_${group.prompt}`"
                        @click="update_url_with_current_group(group)"
                        class="d-flex justify-start text-left">
          <h3 class="text-left d-flex align-center flex-grow-1">
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
          </h3>
          <!-- Archive button -->
          <!-- TODO maybe, play with this more
            eg maybe in edit mode show internal tag-->

        </v-expansion-panel-header>

        <v-expansion-panel-content>
          <attribute_group
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


import axios from 'axios';
import draggable from 'vuedraggable'

import attribute_group from './attribute_group.vue';
import attribute_kind_icons from './attribute_kind_icons.vue';
import attribute_group_new from './attribute_group_new'


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

        openedPanel: null

      }
    },

    watch: {

      // WIP WIP WIP NOT test
      // for "updates in place" to page.
      attribute_template_group_id() {
        this.api_attribute_group_list()
      },

      attribute_group_list_prop() {
        this.attribute_group_list = this.attribute_group_list_prop
      }

    },

    created() {

      // is edit right name? or "from_project" as seperate context / mode here too
      if (this.mode == 'edit') {
       this.api_attribute_group_list("from_project")
      }

      if (this.mode == 'annotate') {
       this.attribute_group_list = this.attribute_group_list_prop
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
            console.log(error)
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

      api_attribute_group_list: function (mode) {

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/attribute/template/list',
          {
            group_id: this.attribute_template_group_id,
            mode: mode

          }).then(response => {

            let attribute_group_list = response.data.attribute_group_list
            this.attribute_group_list = attribute_group_list.sort(
              (a, b) => b.id - a.id);

            this.success = true
            this.loading = false

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
