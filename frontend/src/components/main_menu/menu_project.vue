<template>
  <div>


    <v-flex v-if="!$store.state.project.current.project_string_id
                && $store.state.user.current.security_email_verified == true
                && $store.state.project_list.user_projects_list
                && $store.state.project_list.user_projects_list.length > 0">
      <v-btn color="primary"
              text
              style="text-transform: none !important;"
              @click="$router.push('/projects')">
        <span>
          <v-icon left>folder</v-icon>
          Change Project
        </span>
      </v-btn>
    </v-flex>

    <v-menu v-model="project_menu"
            :nudge-width="150"
            offset-y

            v-if="$store.state.project.current.project_string_id"
            >

      <template v-slot:activator="{ on }">
        <v-btn  v-on="on"
                color="primary"
                id="open_main_menu"
                data-cy="project_menu_dropdown_toggle"
                text
                v-if="$store.state.project.current.project_string_id"
                :disabled="$store.state.user.current.security_email_verified != true || !show_for_user_role">
          <v-icon left> mdi-lightbulb </v-icon>
          Project
          <v-icon right> mdi-chevron-down</v-icon>
        </v-btn>
      </template>


      <v-card>
        <v-layout column>

          <!-- Buttons wrapped in v-flex to help with alignment -->
          <v-flex>
            <v-btn
                color="primary"
                data-cy="main_menu_labels"
                text
                style="text-transform: none !important;"
                :disabled="!$store.state.project.current.project_string_id"
                @click="$router.push('/project/' +
                        $store.state.project.current.project_string_id
                        + '/labels')">
              <v-icon left>mdi-shape-plus</v-icon>
              Schema
            </v-btn>
          </v-flex>

          <v-flex>

            <ahref_seo_optimal href="/white_label_customization/edit">
              <v-btn color="primary"
                    text style="text-transform: none !important;">
                <v-icon left> mdi-puzzle-edit</v-icon>
                White-label Customization
              </v-btn>
            </ahref_seo_optimal>

          </v-flex>

          <v-divider></v-divider>

          <v-flex>
            <v-btn color="primary"
                   data-cy="main_menu_data_explorer"
                   :disabled="!$store.state.project.current.project_string_id"
                    text
                    style="text-transform: none !important;"
                    @click="route_annotate">
              <v-icon left>mdi-draw</v-icon>
              Studio
            </v-btn>
          </v-flex>

          <v-flex>
            <v-btn color="primary"
                   data-cy="main_menu_data_explorer_full_screen"
                   :disabled="!$store.state.project.current.project_string_id"
                    text
                    style="text-transform: none !important;"
                    @click="$router.push(`/studio/annotate/${$store.state.project.current.project_string_id}/explorer`)">
              <v-icon left>mdi-compass</v-icon>
              Query and Explore
            </v-btn>
          </v-flex>

          <v-divider></v-divider>


          <v-flex>
            <v-btn :disabled="!$store.state.project.current.project_string_id"
                   color="primary"
                   text
                   style="text-transform: none !important;"
                   id="upload_section"
                   @click="route_upload">
                <v-icon left>mdi-application-import</v-icon>
                Import
            </v-btn>
          </v-flex>

          <v-flex>
            <v-btn id="export_section" color="primary"
                    text
                   style="text-transform: none !important;"
                   :disabled="!$store.state.project.current.project_string_id"
                    @click="route_project_export">
              <v-icon left>mdi-export</v-icon>
               Export
            </v-btn>
          </v-flex>

          <v-divider></v-divider>

          <v-flex v-if=" $store.state.builder_or_trainer.mode == 'builder'">
            <v-btn :disabled="!$store.state.project.current.project_string_id"
                   color="primary"
                   text
                   style="text-transform: none !important;"
                   @click=" $router.push(`/discussions/?project=${$store.state.project.current.project_string_id}`)">
              <v-icon left>mdi-comment-search</v-icon>
              Discuss
            </v-btn>
          </v-flex>

          <v-flex v-if=" $store.state.builder_or_trainer.mode == 'builder'">
            <v-btn :disabled="!$store.state.project.current.project_string_id"
                   color="primary"
                   text
                   style="text-transform: none !important;"
                   @click=" $router.push(`/report/list?project=${$store.state.project.current.project_string_id}`)">
              <v-icon left>mdi-chart-bar</v-icon>
              Reports
            </v-btn>
          </v-flex>

          <!-- Maintenance / settings type stuff -->

          <v-divider></v-divider>

          <v-flex>
            <v-btn color="primary"
                   text
                   style="text-transform: none !important;"
                   :disabled="!$store.state.project.current.project_string_id"
                    @click="$router.push('/connection/list')">
              <v-icon left>mdi-database-edit</v-icon>
              Connections
            </v-btn>
          </v-flex>


          <v-flex>
            <v-btn color="primary"
                   :disabled="!$store.state.project.current.project_string_id"
                   text
                   style="text-transform: none !important;"
                   @click="route_sync_events_list">
              <v-icon left>mdi-folder-sync</v-icon>
              Stream Events
            </v-btn>
          </v-flex>

          <v-flex v-if=" $store.state.builder_or_trainer.mode == 'builder'">
            <v-btn :disabled="!$store.state.project.current.project_string_id"
                   color="primary"
                   text
                   style="text-transform: none !important;"
                   @click="$router.push('/project/' +
                            $store.state.project.current.project_string_id
                            + '/events') ">
              <v-icon left>mdi-account-clock</v-icon>
              User Events
            </v-btn>
          </v-flex>

          <v-divider></v-divider>


          <!-- This page is confusing -->
          <!--
          <v-flex>
            <v-btn color="primary"
                    text
                   :disabled="!$store.state.project.current.project_string_id"
                    @click="route_project_home">
              <v-icon left>home</v-icon>
              Project page
            </v-btn>
          </v-flex>
          -->


          <v-flex>
            <v-btn color="primary"
                    text
                   style="text-transform: none !important;"
                   :disabled="!$store.state.project.current.project_string_id"
                    @click="route_settings">
              <v-icon left>settings</v-icon>
              Settings
            </v-btn>
          </v-flex>

          <v-divider></v-divider>

          <v-flex v-if=" $store.state.builder_or_trainer.mode == 'builder'">

            <new_flow
              :project_string_id="$store.state.project.current.project_string_id">

            </new_flow>

          </v-flex>

          <v-flex>

            <v-btn color="primary"
                   text
                   style="text-transform: none !important;"
                   @click="$router.push('/project/' + $store.state.project.current.project_string_id + '/workflow/list')">
              <v-icon left>mdi-lan</v-icon>
              My WorkFlows
            </v-btn>

          </v-flex>

          <v-divider></v-divider>

          <v-flex>
            <v-btn color="primary"
                   text
                   style="text-transform: none !important;"
                   @click="$router.push('/projects')">
              <span>
                <v-icon left>folder</v-icon>
                Change Project
              </span>
            </v-btn>
          </v-flex>

        </v-layout>
      </v-card>


    </v-menu>


</div>

</template>

<script lang="ts">

import Vue from "vue";
import new_flow from '../action/action_new_flow.vue'

export default Vue.extend( {
  name: 'main_menu_project',

  components: {
    new_flow : new_flow
  },

  data() {
    return {

      project_menu: false,
      project_manager_dialog: false,
      v_collaborate_new: false
    }
  },
  computed: {
    show_for_user_role: function(){
      if(!this.$store.state.user){
        return false
      }
      if(!this.$store.state.user.current){
        return false
      }
      if(this.$store.state.user.current.is_super_admin){
        return true
      }
      const member_id = this.$store.state.user.current.member_id
      const result = this.$store.getters.member_in_roles(member_id, ['admin', 'editor'])
      return result
    }
  },
  methods: {


    exit_project_manager: function () {
      this.project_manager_dialog = false
    },
    route_project_home: function () {
      this.$router.push('/' + this.$store.state.project.current.user_primary.username +
                        '/' + String(this.$store.state.project.current.project_string_id))
    },
    route_annotate: function () {
      this.$router.push('/studio/annotate/' +
        String(this.$store.state.project.current.project_string_id))

    },
    route_sync_events_list: function () {
      this.$router.push(`/sync-events/list?project_id=${this.$store.state.project.current.project_string_id}`)

    },
    route_changes: function () {
      this.$router.push('/' + this.$store.state.user.current.username
        + '/' + this.$store.state.project.current.project_string_id + '/changes')

    },
    route_upload: function () {
      this.$router.push('/studio/upload/' +
                        this.$store.state.project.current.project_string_id)

    },
    route_project_export() {
      this.$router.push("/project/" + this.$store.state.project.current.project_string_id
        + "/export")
    },
    route_settings() {
      this.$router.push("/project/" + this.$store.state.project.current.project_string_id
        + "/settings")
    }

  }
}
) </script>
