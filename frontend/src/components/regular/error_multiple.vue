<template>
  <div v-cloak
       v-if="error != undefined">

    <v-alert v-if="Object.keys(error).length"
             v-model="show"
             :type="type"
             :width="width"
             :height="height"
             :dense="dense"
             dismissible
             >

      <ul>

        <li v-for="key in Object.keys(error)">

          {{key}}: {{error[key]}}

        </li>

      </ul>

    </v-alert>


    <v-alert v-if="error.user_email_verified ||
                     error.security_email_verified"
              type="info"
              outlined>
      <v_resend_verify_email>
      </v_resend_verify_email>
    </v-alert>



  </div>
</template>

<script lang="ts">

  /*  EXAMPLE USAGE
   *
   *  |||| in html ||||
   *
   *      <v_error_multiple :error="error">
          </v_error_multiple>

   *  |||| in js ||||
   *
   *     error: {}
   *
   *     and when catching an error:
   *
    *   if (error.response.status == 400) {
    *   // CAREFUL this.error should match name
    *   // ie save_error not just error
            this.error = error.response.data.log.error
          }
   *
   *
   */

import Vue from "vue"; export default Vue.extend( {
  name: 'error_multiple',
  props: {
    'error': {
      default: null
    },
    'width': {
      default: undefined
    },
    'height':{
      default: undefined
    },
    'dense': {
      default: false
    },
    'type':{
      default: 'error'
    }
  },
  data() {
    return {
      show: false
    }
  },
  watch:{
    error: function(newVal, oldVal){
      if(newVal){
        this.show = true
      }
      else{
        this.show = false;
      }
    }
  },
  computed: {


  },
  created() {
    if (this.error) {
      this.show = true
    }
  },
  methods: {

  }
}

) </script>
