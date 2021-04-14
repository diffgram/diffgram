<template>
  <div v-cloak>

    <div v-if="!$store.state.user.current.profile_image_url">
      <vue-dropzone ref="edit_profile_photo"
                      id="dropzone_no_profile"
                    :options="dropzoneOptions"
                    v-on:vdropzone-success="upload_success">
      </vue-dropzone>
     </div>

    <v-menu v-if="$store.state.user.current.profile_image_url"
            bottom right
            :close-on-content-click=false>

      <template v-slot:activator="{ on }">

        <v-btn icon v-on="on">

          <!-- Existing / default image -->
          <div v-if="$store.state.user.current.profile_image_url">
            <v-avatar class="pa-4"
                      size="58">
              <img :src="$store.state.user.current.profile_image_url" />
            </v-avatar>
          </div>
          <div v-else>
            <v-icon size="58">account_circle</v-icon>
          </div>

          <!-- We are actually using the
          profile image as the "icon"

          Subtle difference but not support.
          Perhaps in the future we could add an "icon" slot
          inside button_with_menu ie <v-icon> <slot name="icon"> </slot> </v-icon>
            -->

        </v-btn>
      </template>

      <v-card>

        <vue-dropzone ref="edit_profile_photo"
                      data-cy="profile_picture_dropzone"
                      id="dropzone"
                      :options="dropzoneOptions"
                      v-on:vdropzone-success="upload_success">
        </vue-dropzone>
  
      </v-card>

    </v-menu>

  </div>
</template>

<script lang="ts">
// @ts-nocheck

import Vue from "vue";

 export default Vue.extend( {
  name: 'user_profile_image_edit',
  data() {
    return {
      loading: false,

      api_user_update_loading : false,

      dropzoneOptions: {
        url: '/api/user/upload/profile_image',
        maxFiles: 10,
        parallelUploads: 1,
        thumbnailWidth: 150,
        maxFilesize: 30,
        dictDefaultMessage: "Drop profile photo here to upload"
      },

      error_list: [],
      
    }
  },

  computed: {

  },

  created() {
    
  },

  methods: {

    upload_success: function (file) {

      let response = JSON.parse(file.xhr.response)

      console.log(typeof (response), response)
      if (response.success == true) {
        this.$store.commit('set_current_user', response.user)

      }
    }
  }
}

) </script>
