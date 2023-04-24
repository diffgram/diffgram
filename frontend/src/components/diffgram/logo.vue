<template>
  <div v-if="logo">
    <img src="" alt="">
  </div>
</template>

<script lang="ts">

import status from "../status"

import Vue from "vue";
import {get_system_logo} from "../../services/systemConfigs";

export default Vue.extend({

    name: 'admin_install_info',
    components: {
      status
    },
    props: [''],
    data() {
      return {
        logo: {}
      }
    },
    async created() {

      await this.get_system_configs()
    },

    methods: {
      get_system_configs: async function () {
        try {
          const logo_data = await get_system_logo()
          this.logo = logo_data
        } catch (e) {
          console.error(e)
        }
      }
    }
  }
) </script>
