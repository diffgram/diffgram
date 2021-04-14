<template>

<div v-cloak>

<!-- WIP -->

<main_menu  height="100">

  <template slot="second_row">

    <v-toolbar
      dense
      elevation="1"
      fixed
      height="50px"
      >
      <v-toolbar-items>

        <h2 class="pa-1 pr-4"> Connections </h2>

        <tooltip_button
            tooltip_message="New Connection"
            @click="$router.push('/connection/new')"
            icon="add"
            :icon_style="true"
            :large="true"
            color="primary"
            :bottom="true"

                          >
        </tooltip_button>

         <tooltip_button
            tooltip_message="Refresh"
            @click="connection_list_api"
            :loading="loading"
            :icon_style="true"
            icon="mdi-refresh"
            color="primary"
            :large="true"
            :bottom="true"
                        >
        </tooltip_button>


        <!-- Filters

          Could be handy to keep this in the menu button
          In case we want to have this list component embeded
          or in like a pop up or something.


          -->
        <button_with_menu
                tooltip_message="Filters"
                icon="mdi-filter"
                :close_by_button="true"
                offset="x"
                color="primary"
                :commit_menu_status="true"
                          >

          <template slot="content">
            <v-layout>

              <v-select :items="metadata_limit_options"
                        v-model="metadata_limit"
                        label="Results per page"
                        item-value="text"
                        :disabled="loading"
                        @change="item_changed"></v-select>


              </v-layout>

            <!-- May 7, 2020 Hide while WIP -->

            <!--
              <v-select :items="permission_scope_list"
                        v-model="permission_scope"
                        label="Permission Scope"
                        item-value="text"
                        :disabled="loading">
              </v-select>
            -->

          </template>

        </button_with_menu>


      </v-toolbar-items>
    </v-toolbar>
  </template>
</main_menu>


<v-card >

    <v_info_multiple  class="text-left"
                     :info="info">
    </v_info_multiple>

    <!-- LIST LAYOUT -->


    <!--  With regular table the "slots"
        are defined in the headers_selected thing

      -->

    <regular_table
      :item_list="connection_list"
      :column_list="headers_selected"
      :header_list="headers"
      v-model="selected">

      <template slot="name" slot-scope="props">

        <v-btn  @click="$router.push('/connection/' + props.item.id)"
                text
                style="text-transform: none !important;"
                color="primary"

                >
          <h2> {{props.item.name}} </h2>
        </v-btn>

      </template>

      <template slot="integration_name" slot-scope="props">

         <icon_from_regular_list
            :item_list="integration_name_list"
            :value="props.item.integration_name"
            >
         </icon_from_regular_list>
      </template>

      <template slot="permission_scope" slot-scope="props">

        <tooltip_icon
          v-if="permission_scope_icon_dict[props.item.permission_scope]"
          :tooltip_message="permission_scope_icon_dict[props.item.permission_scope].name"
          :icon="permission_scope_icon_dict[props.item.permission_scope].icon"
          :color="permission_scope_icon_dict[props.item.permission_scope].color">
        </tooltip_icon>

      </template>

     <template slot="time_updated" slot-scope="props">
        {{ props.item.time_updated | moment("ddd, MMM Do H:mm a") }}
    </template>

    <template slot="actions" slot-scope="props">

        <tooltip_button
          @click="$router.push('/connection/' + props.item.id)"
          tooltip_message="Edit"
          icon="edit"
          :icon_style="true"

          color="primary">
        </tooltip_button>

    </template>


    </regular_table>

  </v-card>

</div>
</template>

<script lang="ts">
// @ts-nocheck

import axios from 'axios';
import Vue from "vue";
import {create_event} from "../event/create_event";

 export default Vue.extend( {
  name: 'connection_list',
  components: {
   },
   props: {
      'metadata_previous': {
        default: null,
        file: {}
      },
      'request_next_page': {
        default: null
      },
      'view_only_mode': {
      },
      'media_loading': {
       },
      'task': {
       },


    },
  watch: {

  },

  data() {
    return {


      // For permissions on connections
      permission_scope_list: ['project', 'org'],
      permission_scope: 'project',


      integration_name_list: [
        {'display_name': 'Google GCP',
         'name': 'instance',
         'icon': 'mdi-google',
         'color': 'green'
        },
        {'display_name': 'Amazon AWS',
         'name': 'file',
         'icon': 'mdi-aws',
         'color': 'orange'
        },
        {'display_name': 'Microsoft Azure',
         'name': 'event',
         'icon': 'mdi-microsoft-azure', // not coming up for some reason
         'color': 'blue'
        },
        {'display_name': 'ScaleAI',
         'name': 'task',
         'icon': 'mdi-domain',
         'color': 'purple'
        }
      ],

      // mock list example

      item_list : [
        {preview_image: "MOCK ITEM 1 PREVIEW",
         value: "list",
         icon: "mdi-format-list-bulleted"
        },
        {preview_image: "MOCK ITEM 2 PREVIEW",
         value: "icons",
         icon: "mdi-grid"
          }
      ],



      /*
       * TODO feel like some of this
       * could be much more generic ie we use project
       * and org in other places...
       *
       */

      permission_scope_icon_dict: {
        'project': {
            'name': 'Project',
            'icon': 'mdi-lightbulb',
            'color': 'blue'
          },
        'org' : {
            'name': 'Org',
            'icon': 'mdi-domain',
            'color': 'green'
         }
      },


      // WIP WIP WIP WIP

      select_from_metadata: false,

      prevent_refresh_on_layout_change: false,

      layout_view: "icons",
      layout_list : [
        {text: "List",
         value: "list",
         icon: "mdi-format-list-bulleted"
        },
        {text: "Medium Icons",
         value: "icons",
         icon: "mdi-grid"
          }
        ],

      error_inference: {},

      selected: [],

      options : {
        'sortDesc': [true],
        'itemsPerPage': -1
      },
      // -1 for all since we have a limit on how many we show, so makes sense to show all here right?

      info: {},

      loading: false,

      metadata_limit_options: [10, 25, 100, 250],
      metadata_limit: 25,

      request_next_page_flag: false,
      request_next_page_available: true,

      connection_list: [],

      // careful this needs to be exact match for value?
      // default order should match physical order on page too
      // ie so if headers selected here 'period' is 4th then it should be 4th slot too...
      // should be more generic

      headers_selected: [
        "name",
        "integration_name",
        "permission_scope",
        //"member_updated",
        "time_updated",
        "actions"
        ],

      headers_selected_backup : [],  // copied from headers_selected during mounted

      headers: [
        {
          text: "Name",
          align: 'left',
          sortable: true,
          value: 'name'
        },
        {
          text: "Integration",
          align: 'left',
          sortable: false,
          value: 'integration_name'
        },
        // TBD idea of "last used" or something like that
        {
          text: "Permission Scope",
          align: 'left',
          sortable: false,
          value: 'permission_scope'
        },
        /*
        {
          text: "Member Updated",
          align: 'left',
          sortable: false,
          value: 'member_updated'
        },
        */
        {
          text: "Time Updated",
          align: 'left',
          sortable: false,
          value: 'time_updated'
        },
        {
          text: "Actions",
          align: 'left',
          sortable: false,
          value: 'actions'
        }
      ],

      control_key_down : false,
      connection_list_loading: false

    }
  },

  computed: {


    all_selected_count: function () {

      if (this.select_from_metadata == false) {
        return this.selected.length
      }
      else {
        return this.metadata_previous.file_count
      }

    },

    start_index_oneth_index: function() {
      return this.metadata_previous.start_index + 1
    },


  },

  created() {

    // continuing pattern of flexible id selection
    // ie it's not hardwired into API call

    this.project_string_id = this.$store.state.project.current.project_string_id
    this.org_id = this.$store.state.org.current.id

    this.connection_list_api()

  },
  mounted() {

    this.headers_selected_backup = this.headers_selected

    // WIP
    //this.request_media()

    this.loading = false
    this.add_visit_history_event();
  },

  destroyed() {
    window.removeEventListener('keydown', this.keyboard_events_global_down)
    window.removeEventListener('keyup', this.keyboard_events_global_up)

  },

  methods: {
    add_visit_history_event: async function(){
      const event_data = await create_event(this.project_string_id, {
        page_name: 'connection_list',
        object_type: 'page',
        user_visit: 'user_visit',
      })
    },
    keyboard_events_global_down(event) {

    },

    keyboard_events_global_up(event) {

    },

    show_column(column_name){
      return this.headers_selected.includes(column_name)
    },

    connection_list_api() {

      this.connection_list_loading = true

      axios.post('/api/v1/connection/list', {

        permission_scope: this.permission_scope,
        project_string_id: this.project_string_id,
        org_id: this.org_id


      }).then(response => {

        this.connection_list = response.data.connection_list
        this.connection_list_loading = false

      })
      .catch(error => {
        console.log(error);
        this.connection_list_loading = false

      });
    },

    item_changed() {
      this.request_next_page_available = false
    },

    next_page() {
      this.request_next_page_flag = true
      this.request_previous_page_flag = false
      this.$emit('request_media', this.metadata)
    },
    previous_page() {
      /* TODO  trying to follow prior design but this isn't great
       * prefer to share this function...
       *
       */
      this.request_next_page_flag = false
      this.request_previous_page_flag = true
      this.$emit('request_media', this.metadata)

    }

  }
}

) </script>
