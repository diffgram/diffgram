<template>

  <v-dialog v-model="is_open" id="input_payload" :click:outside="close">
    <v-card>
      <v-card-text>
        <action_config_file_upload v-if="action.kind === 'file_upload'"></action_config_file_upload>
      </v-card-text>
    </v-card>
  </v-dialog>

</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
export default Vue.extend({

    name: 'action_config_dialog',
    components: {

    },
    props: ['action'],

    mounted() {

    },

    data() {
      return {
        is_open: false,
      }
    },
    watch: {

    },

    methods: {
      close() {
        this.input = undefined;
        this.is_open = false;
      },
      open() {
        this.is_open = true;
      },
    }
  }
) </script>


<style>
code{
  width: 100%;
  height: 100% !important;
}
</style>
