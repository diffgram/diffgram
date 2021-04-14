<template>
  <div id="follow">


    <v-card>


      <v-badge right large overlap color="primary">
        <span @click="route_follow_list" slot="badge"
              class="image_clickable">
          {{ follow_count }}
        </span>

        <v-btn color="primary" outlined
               @click="follow_toggle">


          <div v-if="loading == false">
            <div v-if="this.follow_state == true">
              <v-icon color="gray" left>mdi-account-remove</v-icon>
              Unfollow
            </div>
            <div v-else>
              <v-icon color="gray" left>mdi-account-plus</v-icon>
              Follow
            </div>
          </div>
        </v-btn>
      </v-badge>




    </v-card>


  </div>
</template>

<script lang="ts">

import axios from 'axios';

  import Vue from "vue"; export default Vue.extend( {
  name: 'follow',
    props: {
      'username': {
        default: null
      },
      'follow_count': {
        default: null
      }
    },
  data () {
    return {
      follow_state: "loading",
      loading: false
    }
  },
  computed: {

  },
  watch: {
    '$route': 'follow_status'
  },
  created() {
    this.follow_status()
  },
  methods: {

    follow_toggle: function () {

      this.loading = true

      axios.post( '/api/username/' + this.$store.state.user.current.username +
                  '/follow/username/' + this.username +
                  '/toggle', {
      })
        .then(response => {
          if (response.data['success'] == true) {

            this.$emit('follow_count', response.data.follow_count)
            this.follow_state = !this.follow_state
          } else {

          }
          this.loading = false
        })
        .catch(error => {
          console.log(error);

        });
    },
    follow_status: function () {

      this.loading = true

      axios.get('/api/username/' + this.$store.state.user.current.username +
                '/follow/username/' + this.username +
                '/status')
        .then(response => {
          if (response.data['success'] == true) {
            this.follow_state = response.data.state
          } else {

          }
          this.loading = false
        })
        .catch(error => {
          console.log(error);

        });
    },

    route_follow_list() {
      this.$router.push('/api/project/' + this.project_string_id +
        '/follow/list')
    }
  }
}
) </script>

