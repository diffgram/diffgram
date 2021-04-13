<template>
  <div id="view_ai_versions">
    <v-container>
      <v-layout container--fluid>
        <v-flex>

          <v-list three-line>

            <template v-for="(item, index) in annotation_project_results">

              <v-list-item avatar
                           ripple
                           @click=""
                           :key="item.title">

                <v-list-item-content @click="">

                  <v-list-item-title>
                    {{ item.name }}
                  </v-list-item-title>

                  <v-list-item-sub-title>
                    Status: {{ item.status }}
                  </v-list-item-sub-title>
                  <div v-if="item.status == 'init'">
                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                  </div>

                </v-list-item-content>


                <v-list-item-action @click="toggle(index)">

                  <v-list-item-action-text>
                    Created: {{ item.created_time }}
                  </v-list-item-action-text>

                  <div v-if="item.status == 'init'">
                    <v-btn text @click="cancel_training(index)">
                      <v-icon left>cancel</v-icon>
                      cancel
                    </v-btn>
                  </div>

                  <v-icon disabled color="grey lighten-1"
                          v-if="selected.indexOf(index) < 0">
                    star_border
                  </v-icon>
                  <v-icon disabled color="yellow darken-2"
                          v-else>star</v-icon>

                </v-list-item-action>

              </v-list-item>

              <v-divider v-if="index + 1 < annotation_project_results.length" :key="item.title"></v-divider>

            </template>
          </v-list>

        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'view_annotation_project_versions',
  props: ['project_string_id'],
  data () {
    return {
    no_redirect: true,
    loading: true,

    selected: [2],

    annotation_project_results: null,
    search_string: null,
    none_found : null
    }
  },
  watch: {
    '$route': 'annotation_project_versions'
  },

  created() {
    this.annotation_project_versions()
  },
  methods: {
    annotation_project_versions: function () {
      axios.get('/api/project/' + String(this.project_string_id) + '/annotation_project/versions')
        .then(response => {
          if (response.data['success'] == true) {

            this.annotation_project_results = response.data['annotation_projects']

          } else {

            this.none_found = true

          }
          this.loading = false
        })
        .catch(error => {
          console.log(error);
        });
    },
    toggle(index) {
      const i = this.selected.indexOf(index)

      if (i > -1) {
        this.selected.splice(i, 1)
      } else {
        this.selected.push(index)
      }
    },
    cancel_training(index) {
      axios.get('/api/project/' + String(this.project_string_id) +
        '/annotation/' + String(this.annotation_project_results[index].id) + '/cancel')
        .then(response => {
          this.annotation_project_versions()
        }).catch(error => { console.log(error); })

    }
  }
}
) </script>

