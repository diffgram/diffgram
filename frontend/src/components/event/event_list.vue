<template>
  <div v-cloak>
    <v-card class="pr-10 pl-10" elevation="0">
      <h1 class="pl-4 pt-4">
      <v-icon color="primary" size="48">mdi-format-list-bulleted-type</v-icon>
        Events:
      </h1>
      <v-layout class="d-flex justify-start pl-8 pb-4 pr-8 align-center"
                style="width: 100%;">
        <v-row>
          <v-col cols="1" class="d-flex align-center">

          <tooltip_button
              @click="refresh_list"
              :loading="loading"
              tooltip_message="Refresh"
              icon="mdi-sync"
              :icon_style="true"
              color="primary">
          </tooltip_button>

          </v-col>

          <v-col cols="2" class="pt-5">

            <diffgram_select
              :item_list="kind_list"
              v-model="kind"
              label="Kind"
              item-value="value"
              :return_object="true"
              :disabled="loading"
              :clearable="true"
            >
            </diffgram_select>

            <member_select
                v-model="member"
                :member_list="$store.state.project.current.member_list">
            </member_select>

          </v-col>
          <v-col cols="3" class="pt-5">
            <date_picker
              @date="date = $event"
              :with_spacer="false"
              :initialize_empty="true"
            >
            </date_picker>
          </v-col>
        </v-row>
      </v-layout>

      <v_error_multiple :error="error">
      </v_error_multiple>

      <regular_table
        :item_list="event_list"
        :column_list="headers_selected"
        :header_list="headers"

        v-model="selected">

        <template slot="time_created" slot-scope="props">
          <p> {{props.item.time_created | moment("ddd, MMM Do H:mm a") }} </p>
        </template>

        <template slot="kind" slot-scope="props">
          <p> {{props.item.kind}} </p>
        </template>

        <template slot="member_id" slot-scope="props">
            <v_user_icon :member_id="props.item.member_id">
            </v_user_icon>
        </template>

        <template slot="description" slot-scope="props">
          <p>
            {{props.item.description}}
          </p>
        </template>

        <template slot="log" slot-scope="props">
          <p> {{props.item.error_log}} </p>

        </template>

      </regular_table>


    </v-card>

  </div>
</template>

<script lang="ts">

  import axios from '../../services/customAxiosInstance';
  import Vue from "vue";
  import {create_event} from "./create_event";

  export default Vue.extend({
      name: 'event_list',

      props: {
        'project_string_id': {
          default: null
        }
      },
      watch: {
        '$route': 'mount'
      },
      data() {
        return {

          error: {},

          member: {
            member_id: null,
          },

          selected: [],
          event_list: [],

          loading: false,

          kind_list:[
            {'name': 'all', 'value': null, 'icon': ''},
            {'name': 'Annotation Update', 'value': 'annotation_update', 'icon': ''},
            {'name': 'new_directory', 'value': 'new_directory', 'icon': ''},
            {'name': 'shared_project', 'value': 'shared_project', 'icon': ''},
            {'name': 'job_launch', 'value': 'job_launch', 'icon': ''},
            {'name': 'file_list_transfer', 'value': 'file_list_transfer', 'icon': ''},
            {'name': 'input_from_packet', 'value': 'input_from_packet', 'icon': ''},
            {'name': 'file_list_update', 'value': 'file_list_update', 'icon': ''},
          ],
          kind: 'All',

          metadata_limit_options: [10, 25, 100, 250],
          metadata_limit: 10,

          request_next_page_flag: false,
          request_next_page_available: true,

          instance_changes: [],
          date:{},
          headers: [
            {
              text: "Time",
              align: 'left',
              sortable: true,
              value: 'time_created'
            },
            {
              text: "Kind",
              align: 'left',
              sortable: false,
              value: 'kind'
            },
            {
              text: "Member",
              align: 'left',
              sortable: false,
              value: 'member_id'
            },
            {
              text: "Description",
              align: 'left',
              sortable: false,
              value: 'description'
            },
            {
              text: "Log",
              align: 'left',
              sortable: false,
              value: 'error_log'
            }
          ],
          headers_selected: [
            "time_created",
            "kind",
            "member_id",
            "description",
            "error_log",
            //"file_id",
            //"input_id"
          ],
        }
      },
      computed: {

      },

      created() {
      },

      mounted() {
        this.add_visit_history_event();
        this.event_list_api()

      },
      methods: {
        add_visit_history_event: async function(){
          const event_data = await create_event(this.$props.project_string_id, {
            page_name: 'event_list',
            object_type: 'page',
            user_visit: 'user_visit',
          })
        },
        item_changed() {
          this.request_next_page_available = false
        },
        refresh_list() {
          this.event_list_api();
        },
        async event_list_api() {

          this.loading = true
          this.error = {}

          try {
            let endpoint = '/api/v1/project/' + this.$props.project_string_id
                + '/event/list'
            const response = await axios.post(endpoint, {
              date_from: this.date.from,
              date_to: this.date.to,
              kind: this.kind ? this.kind.value : null,
              member_id: this.member ? this.member.member_id: null
            })

            if (response.data['event_list'] != null) {

              this.event_list = response.data['event_list']
              this.metadata_previous = response.data['metadata']
            }
          } catch (error) {
            this.error = this.$route_api_errors(error)
          } finally {
            this.loading = false;
          }
        },
      }
    }
  ) </script>
