<template>
  <div>

    <h1> Install Info </h1>

    <ul v-for="[key, group] of Object.entries(install_info)">

      <h2> {{key}} </h2>

      <li v-for="key in Object.keys(group)">

        {{key}}: {{group[key]}}

      </li>

    </ul>


  </div>
</template>

<script lang="ts">

import { get_install_info } from "../../services/configService";

import Vue from "vue"; export default Vue.extend( {

  name: 'admin_install_info',
  components: {
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
