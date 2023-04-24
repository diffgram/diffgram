<template>
  <div class="d-flex flex-column align-center justify-center ma-auto" style="height: 100%;">

    <h1> Logo: </h1>

    <logo :height="200"></logo>

    <v-divider></v-divider>

    <div class="d-flex align-center" style="width: 50%">
      <v-file-input v-model="file" label="Choose a file"></v-file-input>
      <v-btn :disabled="!file" color="primary" class="ml-4" @click="uploadLogo">Upload</v-btn>
    </div>
  </div>
</template>

<script lang="ts">

import { get_install_info } from "../../services/configService";
import status from "../status"
import logo from "./logo.vue"

import Vue from "vue";
import {upload_system_logo} from "../../services/systemConfigs"; export default Vue.extend( {

  name: 'admin_set_logo',
  components: {
    status,
    logo
  },
  props: [''],
  data() {
    return {
      file: null,
      install_info: {}
    }
  },
  async created() {

    const response = await get_install_info()
    this.install_info = response['install_info']
  },
  methods: {
    async uploadLogo() {
      try {
        const [result, err] = await upload_system_logo(this.file)
        if (err){
          console.error(err)
          return
        }
        this.$store.commit('display_snackbar', {
          text: 'Logo successfully.',
          color: 'success'
        })
        this.$store.commit('logo_refresh')
      } catch (error) {
        this.$store.commit('display_snackbar', {
          text:  'Logo upload failed.',
          color: 'error'
        })
        console.error(error)

      }
    },
  }
}

) </script>
