<template>
  <div>


    <v-menu v-model="tasks_menu"
            :nudge-width="150"
            offset-y
            :disabled="false">

      <template v-slot:activator="{ on }">
        <v-btn v-if="$store.state.builder_or_trainer.mode == 'builder'"
               v-on="on"
               :disabled="!$store.state.project || !$store.state.project.current.project_string_id"
               text
        >
          <v-icon left>mdi-brush</v-icon>
          Tasks
          <v-icon right> mdi-chevron-down</v-icon>
        </v-btn>

        <v-btn v-if="$store.state.builder_or_trainer.mode == 'trainer'"
               v-on="on"
               :disabled="$store.state.user.pro_account_approved != true"
               text
               @click="$router.push('/job/list')">
          <v-icon left>mdi-brush</v-icon>
          <v-icon right> mdi-chevron-down</v-icon>
          Tasks
        </v-btn>
      </template>


      <v-card>
        <v-layout column>

          <!-- Buttons wrapped in v-flex to help with alignment -->

          <v-flex>
            <v-btn color="primary"
                   text
                   style="text-transform: none !important;"
                   :disabled="!$store.state.project.current.project_string_id"
                   @click="$router.push('/project/' +
                        $store.state.project.current.project_string_id +
                        '/job/new')">
              <v-icon left>add</v-icon>
              New Tasks
            </v-btn>
          </v-flex>

          <v-flex>
            <v-btn
              color="primary"
              data-cy="main_menu_labels"
              text
              style="text-transform: none !important;"
              :disabled="!$store.state.project.current.project_string_id"
              @click="$router.push('/job/list')">
              <v-icon left>mdi-brush</v-icon>
              Tasks List
            </v-btn>
          </v-flex>

          <v-divider></v-divider>
          <v-flex>

            <v-btn
              color="primary"
              data-cy="main_menu_labels"
              text
              style="text-transform: none !important;"
              :disabled="!$store.state.project.current.project_string_id"
              @click="$router.push('/job/list?type=exam_template')">
              <v-icon left>mdi-shield</v-icon>
              Exams List
            </v-btn>

          </v-flex>
          <v-flex>

            <v-btn
              color="primary"
              data-cy="main_menu_labels"
              text
              style="text-transform: none !important;"
              :disabled="!$store.state.project.current.project_string_id"
              @click="$router.push('/project/' +
                        $store.state.project.current.project_string_id +
                        '/exam/new')">
              <v-icon left>mdi-shield-plus</v-icon>
              New Exam
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

export default Vue.extend({
    name: 'main_menu_tasks',

    components: {
      new_flow: new_flow
    },

    data() {
      return {

        tasks_menu: false,
        project_manager_dialog: false,
        v_collaborate_new: false
      }
    },
    computed: {},
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
