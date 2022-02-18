<template>
  <div id="members_list">

    <v-card-title>

      <h3 v-if="mode == 'project'"
          class="headline">Members</h3>

       <h3 v-if="mode == 'org'"
          class="headline">Members in {{$store.state.org.current.name}} </h3>

      <v-btn color="blue darken-1" text
             href="https://diffgram.readme.io/docs/project"
             target="_blank"
             icon>
        <v-icon>help</v-icon>
      </v-btn>

      <!--
      <v-spacer></v-spacer>
      <v-text-field v-model="search"
                    append-icon="search"
                    label="Search"
                    single-line
                    hide-details></v-text-field>
          -->

    </v-card-title>

    <!-- Only show in project mode till support for removeing from org. -->

    <v-btn  v-if="mode == 'project'"
            @click="api_member_update('REMOVE')"
            color="red"
            class="white--text"
            :loading="api_member_update_loading"
            :disabled="api_member_update_loading || selected.length == 0">
          Remove
        <v-icon right> mdi-shield-remove </v-icon>
    </v-btn>

    <v_error_multiple :error="error">
    </v_error_multiple>

    <v-alert :value="success"
             type="success"
             dismissible>
      Updated.
    </v-alert>

    <!-- We don't appear to be sending a member id so we would want to revisit using
                  item-key="member_id"-->

    <v-data-table :headers="headers"
                  :items="members_list"
                  dense
                  :search="search"
                  class="elevation-1"
                  v-model="selected"
                  item-key="member_id"
                  ref="members_list_table">

      <!-- appears to have to be item for vuetify syntax-->
      <template slot="item" slot-scope="props">

        <tr>
          <td>
            <v-checkbox v-model="props.isSelected"
                        @change="props.select($event)"
                        primary>
            </v-checkbox>
          </td>

          <td v-if="props.item.member_kind == 'human'">
            <v_user_icon :user="props.item">
            </v_user_icon>
          </td>
          <td v-if="props.item.member_kind == 'api'">
            <v-icon>mdi-key</v-icon>
          </td>

          <td v-if="props.item.member_kind == 'human'">
            {{props.item.email}}
          </td>
          <td v-if="props.item.member_kind == 'api'">
           --
          </td>


          <td v-if="props.item.member_kind == 'human'">
            {{props.item.username}}
          </td>
          <td v-if="props.item.member_kind == 'api'">
            {{props.item.client_id}}
          </td>

          <td v-if="props.item.member_kind == 'human'">
            {{props.item.first_name}} {{ props.item.last_name }}
          </td>
          <td v-if="props.item.member_kind == 'api'">
              SDK/API Access User
          <td>

            <div v-if="mode=='project'">
              <div v-if="props.item.member_kind == 'human'">
                {{props.item.permission_level[0]}}
              </div>
            </div>

            <div v-if="mode=='org'">
              <div v-if="props.item.member_kind == 'human'">
                {{props.item.permission_level}}
              </div>
            </div>

            <div v-if="props.item.member_kind == 'api'">
              {{props.item.permission_level}}
            </div>

            </td>
        </tr>

      </template>
    </v-data-table>


  </div>
</template>

<script lang="ts">

import axios from '../../services/customAxiosInstance';

import Vue from "vue"; export default Vue.extend( {
  name: 'members_list',
  props: {
      'project_string_id' : {
        default: null
      },
      'org_id' : {
        default: null
      },
      'mode' : {
        default: "project"   // project or org
      }
  },
  data () {
    return {

    loading: true,
    api_member_update_loading: false,
    search: null,

    error: {},
    success: false,

    none_found: null,

    members_list: [],
    selected: [],

    headers: [
      {
        text: "Select",
        align: 'left',
        sortable: true,
        value: null
      },
      {
        text: "Picture",
        align: 'left',
        sortable: true,
        value: 'member_kind'
      },
      {
        text: "Email",
        align: 'left',
        sortable: true,
        value: 'email'
      },
      {
        text: "Member ID",
        align: 'left',
        sortable: false,
        value: "name"
      },
      {
        text: "Name",
        align: 'left',
        value: null

      },
      {
        text: "Role",
        align: 'left',
        sortable: false,
        value: null
      }
    ]

    }
  },
  watch: {

  },
  created() {
    this.refresh_member_list()
  },
  mounted() {
    var self = this
    this.$store.watch((state) => {
      return this.$store.state.auth.members.refresh
    },
      (new_val, old_val) => {
        self.refresh_member_list()
      },
    )
  },
  methods: {


    api_member_update(mode) {

      this.api_member_update_loading = true
      this.success = false
      this.error = {}  // reset

      axios.post('/api/project/' + this.project_string_id
              + '/share',
        {
          member_list: this.selected,
          mode: mode
        })
        .then(response => {

          this.refresh_member_list()
          this.selected = []    // reset

          this.api_member_update_loading = false
          this.success = true

        }).catch(e => {

          if (e.response)  {
            if (e.response.status == 400) {
                this.error = e.response.data.log.error
            }
            console.error(e)
            this.api_member_update_loading = false
          }
        })
    },

    refresh_member_list: function () {

      /* Caution,
       * select box needs item-key which is member_id
       * there are two methods so we expect both to supply member_id
       * (ie if debuging with project/settings , need to check org/settings
       * too)
       *
       */

      this.loading = true

      if (this.mode == "project") {

        axios.get('/api/project/' + this.project_string_id + '/share/list')
          .then(response => {
            if (response.data['success'] == true) {

              this.members_list = response.data['members_list']
              this.$store.commit('set_current_project_member_list', this.members_list)

            } else {

              this.none_found = true

            }
            this.loading = false
          })
          .catch(error => {


          });

      }

      if (this.mode == "org") {

        axios.get('/api/v1/org/' + this.org_id + '/member/list')
          .then(response => {
            if (response.data['success'] == true) {

              this.members_list = response.data.members_list

            } else {

              this.none_found = true

            }
            this.loading = false
          })
          .catch(error => {


          });
      }
    }
  }
}
) </script>

