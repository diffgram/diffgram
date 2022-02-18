<template>
  <div id="star">


    <v-badge right large overlap color="primary">
      <span @click="route_star_list" slot="badge"
            class="image_clickable">
        {{ star_count }}
      </span>

      <v-btn color="primary" outlined
             @click="star_toggle"
             :disabled="loading"
             >

        <div v-if="this.star_state == 'Starred'">
          <v-icon color="yellow darken-1" left>star</v-icon>
        </div>
        <div v-else>
          <v-icon color="gray" left>star</v-icon>
        </div>

        {{ star_state }}
      </v-btn>
    </v-badge>


  </div>
</template>

<script lang="ts">

import axios from '../../services/customInstance';

  import Vue from "vue"; export default Vue.extend( {
  name: 'star',
    props: {
      'project_string_id': {
        default: null
      },
      'star_count': {
        default: null
      }
    },
  data () {
    return {
      star_state: "loading",
      loading: true
    }
  },
  watch: {
    '$route': 'star_status'
  },
  computed: {

  },
  created() {
    this.star_status()
  },
  methods: {

    star_toggle: function () {

      this.loading = true

      axios.post( '/api/project/' + this.project_string_id +
                  '/username/' + this.$store.state.user.current.username +
                  '/star/toggle', {
      })
        .then(response => {
          if (response.data['success'] == true) {
            this.$emit('star_count', response.data.star_count)
            if (this.star_state == "Starred") {
              this.star_state = "Star"
            } else {
              this.star_state = "Starred"
            }
          } else {

          }
          this.loading = false
        })
        .catch(error => {
          console.log(error);

        });
    },
    star_status: function () {

      this.loading = true

      axios.get('/api/project/' + this.project_string_id +
        '/username/' + this.$store.state.user.current.username +
        '/star/status')
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

    route_star_list() {
      this.$router.push('/api/project/' + this.project_string_id +
        '/star/list')
    }
  }
}
) </script>

