<template>
  <div>

    <h1> Queue Status </h1>

    <v-btn @click="get"
            color="primary"
            data-cy="refresh-input-icon"
            icon
            text
    >
      <v-icon> refresh</v-icon>
    </v-btn>

    <ul v-for="[key, group] of Object.entries(queue_status)">

      <h2> {{key}} </h2>

      <li v-for="key in Object.keys(group)">

        {{key}}: {{group[key]}}

      </li>

    </ul>

    <status> </status>


  </div>
</template>

<script lang="ts">

import { get_queue_status } from "../../services/configService";
import status from "../status"

import Vue from "vue"; export default Vue.extend( {

  name: 'admin_queue_status',
  components: {
    status
  },
  props: [''],
  data() {
    return {
      queue_status: {}
    }
  },
  async created() {

    this.get()

  },
  methods: {
    async get() {
      const response = await get_queue_status()
      this.queue_status = response['queue_status']
    }
  }
}

) </script>
