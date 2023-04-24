<template>
  <div class="d-flex flex-column align-center justify-center">

    <h1> Logo: </h1>

    <logo></logo>

    <v-divider></v-divider>

    <v-btn x-large>Upload New Logo</v-btn>
  </div>
</template>

<script lang="ts">

import { get_install_info } from "../../services/configService";
import status from "../status"
import logo from "./logo.vue"

import Vue from "vue"; export default Vue.extend( {

  name: 'admin_install_info',
  components: {
    status
  },
  props: [''],
  data() {
    return {
      install_info: {}
    }
  },
  async created() {

    const response = await get_install_info()
    this.install_info = response['install_info']
  },
  methods: {

  }
}

) </script>
