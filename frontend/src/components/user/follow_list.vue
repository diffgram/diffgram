<template>
  <div v-cloak>

    <v-card>

      <v-card-title>
        <h3 class="headline">{{follow_type}}</h3>
      </v-card-title>

      <v-container grid-list-md>
        <v-layout >

          <v-flex xs12 sm6>

            <v-list subheader>

              <v-list-item v-for="user in user_list"
                           :key="user.name"
                           
                           >


                <a @click="route_user(user)">
                  {{user.first_name}}
                </a>
   

                <div v-if="user.profile_image_thumb_url">
                  <v-avatar size="48">
                    <img :src="user.profile_image_thumb_url" />
                  </v-avatar>
                </div>
                <div v-else>
                  <v-icon large>account_circle</v-icon>
                </div>

                <v-list-item-action>


                </v-list-item-action>

              </v-list-item>
            </v-list>


          </v-flex>

        </v-layout>
      </v-container>

    </v-card>

  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'follow_list',
  props: {
    'username': {
      default: null
    },
    'follow_type': {
      default: null
    }
  },
  data() {
    return {
      loading: false,

      activity_list: {},

      user_list: []


    }
  },

  computed: {

  },

  watch: {
    '$route': 'follow_list'
  },

  created() {

    this.follow_list()

  },

  methods: {

    follow_list: function () {

      this.loading = true

      axios.get('/api/username/' + this.username +
        '/' + this.follow_type + '/list')
        .then(response => {
          if (response.data['success'] == true) {
            this.user_list = response.data.follow_list.user_list
          } else {

          }
          this.loading = false
        })
        .catch(error => {
          console.log(error);

        });
    },
    route_user: function (user) {
      this.$router.push('/' + user.username)
    }
  }
}

) </script>
