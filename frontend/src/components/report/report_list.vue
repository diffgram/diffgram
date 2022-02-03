<template>

<div v-cloak>

<main_menu  height="100">

  <template slot="second_row">

    <v-toolbar
      dense
      elevation="1"
      fixed
      height="50px"
      >
      <v-toolbar-items>

         <h2 class="pa-1 pr-4"> Reporting </h2>

        <tooltip_button
            tooltip_message="New Report"
            @click="$router.push('/report/new')"
            icon="add"
            :icon_style="true"
            :large="true"
            color="primary"
            :bottom="true"
                          >
        </tooltip_button>

         <tooltip_button
            tooltip_message="Refresh"
            @click="report_template_list_api"
            :loading="loading"
            :icon_style="true"
            icon="mdi-refresh"
            color="primary"
            :large="true"
            :bottom="true"
                        >
        </tooltip_button>


        <tooltip_button
            @click="api_file_update('REMOVE')"
            icon="delete"
            tooltip_message="Remove Selected Files"
            color="red"
            :loading="api_file_update_loading"
            :disabled="api_file_update_loading || selected.length == 0"
            v-if="['annotation'].includes(file_view_mode)"
            :icon_style="true"
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
              <v-select :items="scope_list"
                        v-model="scope"
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
      :item_list="report_template_list"
      :column_list="headers_selected"
      :header_list="headers"
      v-model="selected">

      <template slot="name" slot-scope="props">

        <v-btn  @click="$router.push('/report/' + props.item.id)"
                text
                style="text-transform: none !important;"
                color="primary"
                :disabled="!$store.state.user.current.is_super_admin
                    && props.item.diffgram_wide_default"
                >
          <h2> {{props.item.name}} </h2>
        </v-btn>

      </template>

      <template slot="item_of_interest" slot-scope="props">
        <tooltip_icon
          :tooltip_message="item_of_interest_dict[props.item.item_of_interest].name"
          :icon="item_of_interest_dict[props.item.item_of_interest].icon"
          :color="item_of_interest_dict[props.item.item_of_interest].color">
        </tooltip_icon>
      </template>

      <template slot="group_by" slot-scope="props">

         <icon_from_regular_list
            :item_list="group_by_list"
            :value=" props.item.group_by"
            >
         </icon_from_regular_list>

      </template>

      <template slot="period" slot-scope="props">

         <icon_from_regular_list
            :item_list="period_list"
            :value=" props.item.period "
            >
         </icon_from_regular_list>

      </template>

      <template slot="scope" slot-scope="props">

        <tooltip_icon
          :tooltip_message="scope_icon_dict[props.item.scope].name"
          :icon="scope_icon_dict[props.item.scope].icon"
          :color="scope_icon_dict[props.item.scope].color">
        </tooltip_icon>

      </template>

     <template slot="time_updated" slot-scope="props">
        {{ props.item.time_updated | moment("ddd, MMM Do H:mm a") }}
    </template>

    <template slot="actions" slot-scope="props">

        <tooltip_button
          @click="$router.push('/report/' + props.item.id)"
          tooltip_message="Edit"
          icon="edit"
          :icon_style="true"
          :disabled="!$store.state.user.current.is_super_admin
                    && props.item.diffgram_wide_default"
          color="primary">
        </tooltip_button>

    </template>

    <!-- Careful slot name needs to match headers selected ? -->

    <template slot="is_visible_on_report_dashboard" slot-scope="props">

      <!-- Could do a button here in future for "fast" change -->

        <tooltip_icon
          v-if="props.item.is_visible_on_report_dashboard"
          icon="mdi-eye"
          color="primary">
        </tooltip_icon>

        <tooltip_icon
          v-if="!props.item.is_visible_on_report_dashboard"
          icon="mdi-eye-off"
          color="grey">
        </tooltip_icon>

    </template>

      <template slot="diffgram_wide_default" slot-scope="props">

        <tooltip_icon
          v-if="props.item.diffgram_wide_default"
          icon="mdi-check-circle"
          color="primary">
        </tooltip_icon>
    </template>


    </regular_table>

  </v-card>

</div>
</template>

<script lang="ts">
// @ts-nocheck

import axios from 'axios';
import icon_from_regular_list from '../../components/regular/icon_from_regular_list.vue'

import Vue from "vue";
import {create_event} from "../event/create_event";

 export default Vue.extend( {
  name: 'report_list',
  components: {
    icon_from_regular_list
   },
   props: {
      'current_file': {
        default: null
      },
      'video_mode': {
        default: null  //  this was a bool, but we aren't using it here?
      },
      'file_view_mode': {
        default: null  // home, task, changes, annotation
      },
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


      // For permissions on reports
      scope_list: ['project', 'org'],
      scope: 'project',

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

      /* Slightly different format, accessing via key
       * Alterantive is to do a find operation on array I guess...
       * we are using the key as the lower case name
       * slight duplicate ie writing user twice
       * but that seems cleaner then a bunch of functions to
       * convert lower/upper maybe?
       */
      item_of_interest_dict: {
        'user': {
            'name': 'User',
            'icon': 'mdi-account-circle',
            'color': 'blue'
          },
        'instance' : {
           'name': 'Instance',
           'icon': 'mdi-format-paint',
           'color': 'green'
          },
        'file': {
           'name': 'File',
           'icon': 'mdi-file',
           'color': 'orange'
          },
        'event' : {
           'name': 'Event',
           'icon': 'mdi-calendar-star',
           'color': 'pink'
          },
        'task' : {
          'name': 'Task',
          'icon': 'mdi-flash-circle',
         'color': 'purple'
        }
      },


      /*
       * TODO feel like some of this
       * could be much more generic ie we use project
       * and org in other places...
       *
       */

      scope_icon_dict: {
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

      report_template_list: [],

      // careful this needs to be exact match for value?
      // default order should match physical order on page too
      // ie so if headers selected here 'period' is 4th then it should be 4th slot too...
      // should be more generic

      headers_selected: [
        "name",
        "item_of_interest",
        "group_by",
        "period",
        "scope",
        //"member_updated",
        "time_updated",
        "actions",
        "is_visible_on_report_dashboard",
        "diffgram_wide_default"
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
          text: "Report On",
          align: 'left',
          sortable: false,
          value: 'item_of_interest'
        },
        {
          text: "Group By",
          align: 'left',
          sortable: false,
          value: 'group_by'
        },
        {
          text: "Period",
          align: 'left',
          sortable: false,
          value: 'period'
        },
        {
          text: "Scope",
          align: 'left',
          sortable: false,
          value: 'scope'
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
        },
        {
          text: "Visible",
          align: 'left',
          sortable: false,
          value: 'is_visible_on_report_dashboard'
        },
        {
          text: "Default",
          align: 'left',
          sortable: false,
          value: 'diffgram_wide_default'
        }
      ],

      control_key_down : false,


      report_template_list_loading: false,

      // Duplicate from report.vue
      group_by_list: [
        {'display_name': 'Date',
         'name': 'date',
         'icon': 'mdi-calendar',
         'color': 'primary'
        },
        {'display_name': 'User',
         'name': 'user',
         'icon': 'mdi-account-circle',
         'color': 'blue'
        },
        {'display_name': 'Job',
         'name': 'job',
         'icon': 'mdi-lightbulb-group',
         'color': 'green'
        },
        {'display_name': 'Label',
         'name': 'label',
         'icon': 'mdi-format-paint',
         'color': 'pink'
        }
      ],

      // Duplicate from report.vue
      period_list: [
        {'display_name': 'Last 30 Days',
         'name': 'last_30_days',
         'icon': 'mdi-history',
         'color': 'primary'
        },
        {'display_name': 'All',
         'name': 'all',
         'icon': 'mdi-select-all',
         'color': 'primary'
        }
      ]

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

  async created() {

    // continuing pattern of flexible id selection
    // ie it's not hardwired into API call
    const query_project_id =  this.$route.query.project
    this.project_string_id = this.$store.state.project.current.project_string_id
    if(query_project_id && query_project_id !== this.project_string_id){
      const project_data = await this.get_project_data(query_project_id)
      this.$store.commit('set_project', project_data)
      this.project_string_id = query_project_id;
    }

    this.org_id = this.$store.state.org.current.id

    this.report_template_list_api()

  },
  mounted() {

    this.headers_selected_backup = this.headers_selected

    // WIP
    //this.request_media()
    this.add_visit_history_event();
    this.loading = false

  },

  destroyed() {
    window.removeEventListener('keydown', this.keyboard_events_global_down)
    window.removeEventListener('keyup', this.keyboard_events_global_up)

  },

  methods: {
    add_visit_history_event: async function(){
      this.project_string_id = this.$store.state.project.current.project_string_id
      const event_data = await create_event(this.project_string_id, {
        page_name: 'reports_dashboard',
        object_type: 'page',
        user_visit: 'user_visit',
      })
    },
    get_project_data: async function(project_string_id){
      try{
        const response = await axios.get(`/api/project/${project_string_id}/view`)
        if(response.data){
          return response.data.project
        }
      }
      catch (error) {
        console.error(error)
      }
    },
    keyboard_events_global_down(event) {

    },

    keyboard_events_global_up(event) {

    },

    show_column(column_name){
      return this.headers_selected.includes(column_name)
    },

    report_template_list_api() {

      this.report_template_list_loading = true

      axios.post('/api/v1/report/template/list', {

        scope: this.scope,
        project_string_id: this.project_string_id,
        org_id: this.org_id


      }).then(response => {

        this.report_template_list = response.data['report_template_list']
        this.report_template_list_loading = false

      })
      .catch(error => {
        console.log(error);
        this.report_template_list_loading = false

      });
    },

    change_file_request(file) {

      if (this.control_key_down == true) {
        this.select_from_something(file)
        return
      }

      this.$emit('change_file', file)


    },

    item_changed() {
      this.request_next_page_available = false
    },
    request_media() {
      this.request_next_page_flag = false
      this.request_previous_page_flag = false
      this.request_next_page_available = true

      this.select_from_metadata = false
      this.selected = []

      this.$emit('request_media', this.metadata)
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

    },
    remove_function: function (file) {

      this.selected = [file]

      this.api_file_update('REMOVE')

      // handled by api_file_update() so not needed
      // but this may have been cleaner way to do it for single file
      // this.$emit('remove_file_request', file)

    },
    annotation_example_toggle_function(image, index) {

      axios.post('/api/project/' + this.project_string_id
        + '/images/annotation_example_toggle',
        { image: image })
        .then(response => {
          if (response.data.success = true) {

            this.$emit('annotation_example_image_toggle_ui', index)

          }
        }).catch(e => { console.log(e) })
    },

    get_video_single_detail(video_id) {
      axios.get('/api/project/' + this.project_string_id
        + '/video/single/' + video_id + '/view')
        .then(response => {
          if (response.data.success = true) {


            this.current_video = response.data.video
            this.$emit('current_video_update', this.current_video)

          }
        }).catch(e => { console.log(e) })

    },

    api_file_update(mode) {

      this.api_file_update_loading = true
      this.info = {}  // reset

      axios.post('/api/v1/project/' + this.project_string_id
              + '/file/update',
        {
          directory_id: this.$store.state.project.current_directory.directory_id,
          file_list: this.selected,
          mode: mode,
          select_from_metadata: this.select_from_metadata,
          metadata_proposed: this.metadata_previous

        })
        .then(response => {


          this.request_media()
          this.info = response.data.log.info
          this.selected = []    // reset

          this.api_file_update_loading = false

        }).catch(e => {
          console.log(e)
          this.api_file_update_loading = false

        })

  },
    add_to_inference(file) {

      // TODO I think this method is deprecated??

      axios.post('/api/project/' + this.project_string_id
        + '/file/' + file.id
        + '/inference/add',
        {})
        .then(response => {
          if (response.data.success = true) {
            //this.run_FAN_success = true
          }

          // Until we have better system
          //this.run_FAN_disabled = false
        }).catch(e => {
          console.log(e)
          this.run_FAN_disabled = false
        })

    }

  }
}

) </script>
