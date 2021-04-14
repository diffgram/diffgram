<template>
  <div v-cloak>
    <v-card>

      <v_search_query>
      </v_search_query>


      <v-card-title>
        Results (Public projects only)
      </v-card-title>


      {{results_length}}

      <v-data-table v-bind:headers="header"
                    :items="results_list"
                    class="elevation-1"
                    item-key="project_string_id"
                    hide-default-footer>

        <!-- appears to have to be item for vuetify syntax-->
        <template slot="item" slot-scope="props">

          <tr>
            <td>

              <a @click="route_to_user(props.item)">
                {{props.item.user_primary.username}}
              </a>

            </td>
            <td>

              <a @click="route_to_project(props.item)">
                {{props.item.name}}
              </a>

            </td>

            <td>
              {{props.item.description}}

            </td>
            <td>

              {{props.item.images_count}}

            </td>
            <td>

              {{props.item.labels_count}}

            </td>
            <td>

              {{props.item.star_count}}

            </td>

          </tr>

        </template>
      </v-data-table>


    </v-card>

  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'search_results',
  props: {

  },
  data() {
   return {

      tag_list: [],

      results_list: [],
      results_length: null,

     header: [
           {
             text: "User",
             align: 'left',
             sortable: false
           },
          {
            text: "Project",
            align: 'left',
            sortable: false,
          },
          {
            text: "Description",
            align: 'left',
            sortable: false,
           },
           {
             text: "Images",
             align: 'left',
             sortable: true,
             value: "images_count"
           },
           {
             text: "Labels",
             align: 'left',
             sortable: true,
             value: "labels_count"
           },
          {
            text: "Star count",
            align: 'left',
            sortable: true,
            value: "star_count"
          }
        ],

      loading: false

    }
  },
  computed: {


  },
  watch: {
    '$route'() {
      this.tag_list = this.$route.query["tags"]
      this.search()
    }
  },
  created() {

    this.tag_list = this.$route.query["tags"]
    this.search()

  },
  methods: {

    route_to_user(result) {

      this.$router.push("/" + result.user_primary.username
      )

    },

    route_to_project(result) {

      this.$router.push("/" + result.user_primary.username +
                        "/" + result.project_string_id
        )

    },
    search: function () {

      this.loading = true
      this.results_list = []
      this.results_length = null

      axios.post('/api/search/project', {

          'tag_list': this.tag_list
        })
        .then(response => {
          if (response.data['success'] == true) {

            this.results_list = response.data.results_list
            this.results_length = response.data.results_length

          } else {

          }
          this.loading = false
        })
        .catch(error => {
          console.log(error);

        });
    }
  }
}

) </script>
