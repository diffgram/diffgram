<template>

  <v-dialog v-model="is_open" id="input_payload" :click:outside="close" width="800px">
    <v-card elevation="1" class="pa-4" >
      <v-card-title class="d-flex justify-center flex-column">
        <img class="text-center mt-4 mb-4"
             height="150"
             width="400"
             src="https://github.com/diffgram/diffgram/raw/master/github_assets/DiffgramLogoVECTOR.svg" alt="">
        <h1 class="font-weight-medium">
          You've Reached Your Free Plan Limit!
        </h1>
      </v-card-title>
      <v-card-text class="d-flex align-center justify-center flex-column ">
        <h1 class="mt-6 text-center font-weight-light">{{message}}</h1>

        <h2 class="mt-6 warning--text">Details: </h2>
        <h3 class="font-weight-light warning--text">
          {{details}}
        </h3>

        <h2 class="text-center ma-auto mt-8" style="color: #4caf50">Upgrade to Premium to remove all limits!</h2>
        <v-btn

          @click="go_to_order_page"
          outlined
          x-large
          class="mt-4"
          color="success">
          <v-icon left>mdi-star-shooting</v-icon>
          Upgrade
        </v-btn>

      </v-card-text>
    </v-card>
  </v-dialog>

</template>

<script lang="ts">

  import axios from 'axios';
  import labels_view from '../../components/annotation/labels_view'
  import v_upload_large from '../upload_large'
  import Vue from "vue";
  import CodeDiff from 'vue-code-diff/dist/vue-code-diff'

  export default Vue.extend({

      name: 'input_payload_dialog',
      components: {
        labels_view: labels_view,
        CodeDiff: CodeDiff,
        v_upload_large: v_upload_large
      },
      props: ['message', 'details'],

      mounted() {

      },

      data() {
        return {
          is_open: false,
        }
      },
      methods: {
        go_to_order_page: function(){
          if(window.location.host === 'diffgram.com'){
            window.open(`https://diffgram.com/order/premium`, '_blank')

          }
          else{
            window.open(`https://diffgram.com/order/premium?install_fingerprint=${this.$store.state.user.current.install_fingerprint}&email=${this.$store.state.user.current.email}`, '_blank')

          }
          // window.open(`https://diffgram.com/order/premium?install_fingerprint=${this.$store.state.user.current.install_fingerprint}`, '_blank')

        },
        close(){
          this.input = undefined;
          this.is_open = false;
        },
        open() {
          this.is_open = true;
        },
      }
    }
  ) </script>
