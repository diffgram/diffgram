<template>
  <div v-cloak>

    <v-alert type="info"
             v-if="Object.keys(info).length"
             @input="$emit('input')"
             dismissible
             >
    <!-- TODO, this loses event info which may be bad-->
      <ul>

        <li v-for="key in Object.keys(info)">

          {{info[key]}}

        </li>

      </ul>

    </v-alert>

  </div>
</template>

<script lang="ts">

/*
 USAGE

Similar to regular error

  <v_info_multiple :info="info">
  </v_info_multiple>

Include the info dict in data()
reset it prior to calling api
load into it from call ie
     this.info = response.data.log.info


*/

import Vue from "vue";

export default Vue.extend( {
  name: 'info_multiple',
  props: {
    'info': {
      default: {}
    }
  },
  data() {
    return {
    }
  },
  created() {


  },
  methods: {

  }
}

) </script>
