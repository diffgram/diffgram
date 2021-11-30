
<template>

  <div  v-if="$store.state.user.logged_in==false">
    <ahref_seo_optimal href="/user/login/">
      <v-btn text
             style="text-transform: none !important;"
             >
        Login
      </v-btn>
    </ahref_seo_optimal>
  </div>

  <div v-else>

    <!-- User Profile Icon Menu -->
    <v-menu
      bottom
      left
      @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"
      >

      <template v-slot:activator="{ on }">

        <v-btn
          @click="$store.commit('set_user_is_typing_or_menu_open', true)"
          icon
          v-on="on"
          colour="primary">

          <div v-if="$store.state.user.current.profile_image_thumb_url">
            <v-avatar size="36">
              <img :src="$store.state.user.current.profile_image_thumb_url" />
            </v-avatar>
          </div>
          <div v-else>
            <v-icon  large>account_circle</v-icon>
          </div>

        </v-btn>

      </template>
      <v-card>

        <v-card-title primary-title>
          <div>
            <h3 class="headline mb-1"> {{ $store.state.user.current.email }}</h3>
            <div></div>
          </div>
        </v-card-title>

        <v-card-actions>
          <!-- Disabled profile is WIP -->
          <!--
          <v-btn @click="profile" text color="blue">Profile</v-btn>
              -->

            <!-- Only show menu if a builder mode is enabled
           (new users have no mode enabled-->


          <v-btn v-if="$store.state.user.current.email"
                 @click="edit"
                 text
                 color="primary">
            <v-icon left>edit</v-icon>
          Edit
          </v-btn>

          <v-btn @click="logout"
                 text
                 color="primary">
            <v-icon left>logout</v-icon>
          Logout
          </v-btn>

        </v-card-actions>

      </v-card>

    </v-menu>
  </div>

</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue"; export default Vue.extend( {
  name: 'profile_in_menu',
  components: {

  },
  data() {
    return {

    }
  },
  methods: {
    logout: function () {
      axios.get('/user/logout')
        .then(response => {

          this.$store.dispatch('log_out')
          this.$router.push('/user/login');

        })
        .catch(error => {
          console.error(error);
        });
    },
    edit: function () {
      this.$router.push('/user/edit/');
    },
    profile: function () {
      this.$router.push('/' + this.$store.state.user.current.username);
    }
  }
}
) </script>
