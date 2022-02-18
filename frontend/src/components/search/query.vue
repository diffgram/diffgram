<template>
  <div v-cloak>



    <v-combobox v-model="selected_tag_list"
                :items="available_tags_list"
                :search-input.sync="search"
                hide-selected
                label="Search by tag"
                multiple
                small-chips>

      <template slot="no-data">
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>
              No tags matching "<strong>{{ search }}</strong>". Press <kbd>enter</kbd> to search anyway.
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </template>
    </v-combobox>

    <v-btn large color="primary"
           class="mx-0"
           @click="route_to_results_page">
      Search
    </v-btn>




  </div>
</template>

<script lang="ts">

import axios from '../../services/customInstance';

import Vue from "vue"; export default Vue.extend( {
  name: 'search_query',
  props: {

  },
  data() {
    return {


      available_tags_list: [],
      selected_tag_list: [],
      search: null,

      loading: false

    }
  },
  watch: {
    model(val) {
      if (val.length > 5) {
        this.$nextTick(() => this.model.pop())
      }
    }
  },
  computed: {


  },
  created() {

    if (this.$route.query["tags"] != undefined) {
      if (this.$route.query["tags"] != "") {
        this.selected_tag_list = this.$route.query["tags"].split(",")
      }
    }
    this.get_available_tags()

  },
  methods: {

    route_to_results_page() {

      this.$router.push('/search?tags=' + this.selected_tag_list)


    },
    get_available_tags: function () {

      this.loading = true

      axios.get('/api/tags/public/list')
        .then(response => {
          if (response.data['success'] == true) {
            this.available_tags_list = response.data.tag_list
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
