<template>

  <div v-if="logo">
    <img :src="logo.url_signed"
         :height="height ? `${height}px` : undefined"
         :width="width ? `${width}px` : undefined"
    >
  </div>
  <div v-else>
    <img src="https://storage.googleapis.com/diffgram-002/public/logo/diffgram_logo_word_only.png"
         :height="height ? `${height}px` : undefined"
         :width="width ? `${width}px` : undefined"
    />
  </div>
</template>

<script lang="ts">

import status from "../status"

import Vue from "vue";
import {get_system_logo} from "../../services/systemConfigs";

export default Vue.extend({

    name: 'Logo',
    components: {
      status
    },
    props: ['height', 'width'],
    data() {
      return {
        logo: undefined
      }
    },

    async created() {

      await this.get_system_configs()
    },
    watch: {
      logo_refresh: function(){
        console.log('REFRESH LOGOOOO')
        this.get_system_configs()
      }
    },
    methods: {
      get_system_configs: async function () {
        try {
          const [logo_data, err] = await get_system_logo()
          if (err) {
            console.error(err)
            return
          }
          this.logo = logo_data
        } catch (e) {
          console.error(e)
        }
      }
    },
    computed: {
      logo_refresh: function () {
        return this.$store.state.system.logo_refresh;
      }
    }
  }
) </script>
