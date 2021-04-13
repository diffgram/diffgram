<template>
  <div v-cloak>
 

    <v-combobox v-model="selected_tags"
                :items="available_tags_list"
                :search-input.sync="search"
                hide-selected
                label="Add or edit tags"
                @blur="update_tags"
                multiple
                small-chips>

      <template slot="no-data">
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>
              No tags matching "<strong>{{ search }}</strong>".
              Press <kbd>enter</kbd> to create anyway.
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </template>


    </v-combobox>


  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'tags',
  props: {
    'project_string_id': {
      default: null
    },
    'tag_list': {
      default: null
    }

  },
  data() {
    return {

      available_tags_list: [],
      selected_tags: [],
      search: null,

      loading: false

    }
  },
  watch: {
    selected_tags(val) {
      if (val.length > 5) {
        this.$nextTick(() => this.selected_tags.pop())
      }
    },
    '$route': 'created'
  },

  computed: {


  },
  created() {

    this.created()

  },
  methods: {

    created: function () {

      this.available_tags_list = []
      this.selected_tags = []

      this.get_project_tags()
      this.get_available_tags()

    },

    update_tags: function () {

      this.loading = true

      axios.post( '/api/project/' + this.project_string_id +
                  '/tags/update',
        {
          'tag_list': this.selected_tags
        })
      .then(response => {
        if (response.data['success'] == true) {

          this.star_state = response.data.state

        } else {

        }
        this.loading = false
      })
      .catch(error => {
        console.log(error);

      });
    },

    get_project_tags: function () {

      this.loading = true

      axios.get('/api/project/' + this.project_string_id +
                '/tags/list')
        .then(response => {
          if (response.data['success'] == true) {
            this.selected_tags = response.data.tag_list
          } else {

          }
          this.loading = false
        })
        .catch(error => {
          console.log(error);

        });
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
