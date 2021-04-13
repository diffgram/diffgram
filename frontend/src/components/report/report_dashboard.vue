<template>
  <div v-cloak>

    <v_error_multiple :error="error">
    </v_error_multiple>

    <v-card v-if="report_template_list.length > 0" elevation="0">

      <v-skeleton-loader
        :loading="loading"
        type="card@3">

        <template>
          <v-container class="pa-20">
            <v-row>
              <v-col
                v-for="(item, index) in report_template_list"
                :key="item.id"
              >
                <v-card
                  width="400"
                  :accesskey="item.name"
                >

                  <!-- TODO could at click go to report... -->
                  <v-card-title
                    @click=""
                  >
                    {{item.name}}

                    <v-spacer></v-spacer>

                    <!-- TODO different handling if it's a default
                      report. -->

                    <tooltip_button
                        tooltip_message="Edit Report"
                        @click="$router.push('/report/' + item.id)"
                        icon="edit"
                        :text_style="true"
                        :disabled="!$store.state.user.current.is_super_admin"
                        color="primary">
                    </tooltip_button>

                   </v-card-title>

                  <report
                    :report_template_id=item.id
                    :may_edit="false"
                          >
                  </report>


                  <v-card-text class="text--primary">

                  </v-card-text>
                </v-card>

              </v-col>
            </v-row>
          </v-container>
        </template>

      </v-skeleton-loader>
    </v-card>
  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue";

import report from "./report.vue"
import {create_event} from "../event/create_event";

export default Vue.extend( {
  name: 'report_dashboard',
  components: {
    report
  },
  props: {
      'report_dashboard_id' : {
        type: Number,
        default: null
      }
  },
  data() {
    return {

      report_template_list: [],
      loading: true,
      error: {},
      mode: null

    }
  },
  computed: {
  },
  watch: {
  },
  created() {

    this.refresh()

  },
  methods: {

    refresh: function () {

      this.loading = true

      if (!this.mode){
        this.refresh_from_project_default()
      }
    },

    refresh_from_project_default: function () {

      if (!this.$store.state.project.current.project_string_id) {
        // some cases where we don't have this, if that's true for some reason
        // dont' bother running since then it shows a permission error which looks silly
        this.loading = false
        return
      }

      axios.post('/api/v1/report/template/list', {
        report_dashboard_id: this.report_dashboard_id,

        // needs this for permissions.
        project_string_id: this.$store.state.project.current.project_string_id,

        only_is_visible_on_report_dashboard: true

      }
      ).then(response => {

        this.loading = false
        this.report_template_list = response.data.report_template_list

      })
      .catch(error => {
        console.log(error);
        this.error = this.$route_api_errors(error)
      });

    }

  }
}

)
</script>

<style>

</style>
