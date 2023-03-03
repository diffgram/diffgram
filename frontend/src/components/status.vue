<template>
  <div>


    <div v-if="show_detail == false">
      <v_error_multiple :error="default_error">
      </v_error_multiple>

      <v_error_multiple :error="walrus_error">
      </v_error_multiple>
    </div>

    <div v-if="show_detail == true">
      <h1> Status </h1>

      <standard_button
        tooltip_message="Refresh"
        @click="check_all"
        :disabled="default_loading || walrus_loading"
        color="primary"
        icon="mdi-refresh"
        :icon_style="true"
        :bottom="true"
      >
      </standard_button>

      <v-card-title> Default Service </v-card-title>
      <v_error_multiple :error="default_error">
      </v_error_multiple>
      <v-alert v-if="default_success" type="success">
        Default is ok.
      </v-alert>
      <v-progress-linear
        v-if="default_loading"
        indeterminate
        rounded
        height="3"
        attach
      ></v-progress-linear>

      <v-card-title> Walrus Service </v-card-title>
      <v_error_multiple :error="walrus_error">
      </v_error_multiple>
      <v-alert v-if="walrus_success" type="success">
        Walrus is ok.
      </v-alert>
      <v-progress-linear
        v-if="walrus_loading"
        indeterminate
        rounded
        height="3"
        attach
      ></v-progress-linear>

      <v-container fluid class="d-flex justify-start align-center">
        <h2 class="font-weight-light">
        Last checked: {{formatted_time}}
        </h2>
      </v-container>
    </div>

  </div>
</template>

<script lang="ts">

import { get_walrus_status, get_default_status } from "../services/configService";

import Vue from "vue"; export default Vue.extend( {

  name: 'status',
  components: {
  },

  props: {
    'show_detail': {
      default: false,
      type: Boolean
    }
  },

  data() {
    return {
      default_error: {},
      walrus_error: {},
      default_loading : false,
      walrus_loading: false,
      default_success: false,
      walrus_success: false,
      time: 0
    }
  },
  async created() {

    if (this.$route.path == '/status') {
      this.$props.show_detail = true
    }

    this.check_all()
  },
  computed: {
    formatted_time: function(){
      var date = new Date(0);
      date.setSeconds(this.time); // specify value for SECONDS here
      var timeString = date.toISOString().substr(11, 8);
      return timeString
    }
  },
  methods: {


    async check_all(){
      this.time = 0
      this.start()
      this.check_default()
      this.check_walrus()
    },

    start: function(){
      clearTimeout(this.timer);
      this.timer = setTimeout(() => {
        this.time += 1;
        this.start()
      }, 1000)
    },

    async check_generic(api) {
      let result = await api()
      let success = undefined
      let error = undefined
      if (result.status == 200) {
        success = true
      } else{
        error = this.$route_api_errors(result)
      }
      return [success, error]
    },

    async check_default() {
      this.default_loading = true
      this.default_success = undefined
      this.default_error = undefined
      let result = await this.check_generic(get_default_status)
      this.default_success = result[0]
      this.default_error =  result[1]
      this.default_loading = false
    },

    async check_walrus() {
      this.walrus_loading = true
      this.walrus_success = undefined
      this.walrus_error = undefined
      let result = await this.check_generic(get_walrus_status)
      this.walrus_success = result[0]
      this.walrus_error =  result[1]
      this.walrus_loading = false
     }
  }
}

) </script>
