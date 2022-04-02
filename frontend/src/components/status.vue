<template>
  <div>

    <h1> Status </h1>

    <tooltip_button
      tooltip_message="Refresh"
      @click="check_walrus(), check_default()"
      :loading="default_loading"
      color="primary"
      icon="mdi-refresh"
      :icon_style="true"
      :bottom="true"
    >
    </tooltip_button>

    {{default_error}}
    {{walrus_error}}

  </div>
</template>

<script lang="ts">

import { get_walrus_status, get_default_status } from "../services/configService";

import Vue from "vue"; export default Vue.extend( {

  name: 'status',
  components: {
  },
  props: {},

  data() {
    return {
      default_error: {},
      walrus_error: {},
      default_loading : false,
      walrus_loading: false
    }
  },
  async created() {

    this.check_walrus()
    this.check_default()
  },
  methods: {

    async check_walrus() {
      this.walrus_error = await get_walrus_status()
    },

    async check_default() {
      this.default_error = await get_default_status()
    }
  }
}

) </script>
