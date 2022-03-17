<template>

  <v-dialog v-model="is_open" id="input_payload" :click:outside="close">
    <v-card elevation="1">
      <v-card-title>Input Payload:</v-card-title>
      <v-card-text>
        <v-progress-circular indeterminate v-if="loading"></v-progress-circular>
        <v-container fluid v-if="input && input.frame_packet_map">
          <ssh-pre copy-button dark language="JSON" label="JSON">{{ input.frame_packet_map | pretty }}</ssh-pre>

        </v-container>
        <v-container fluid v-if="input && input.instance_list">
          <ssh-pre copy-button dark language="JSON" label="JSON">{{ input.instance_list | pretty }}</ssh-pre>

        </v-container>
        <v-container fluid v-if="input && !input.instance_list && !input.frame_packet_map" class="d-flex justify-center ma-12">
          <h2>
            <v-icon x-large>mdi-dolly</v-icon>
            Empty Payload
          </h2>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>

</template>

<script lang="ts">

import axios from '../../services/customInstance';
import labels_view from '../../components/annotation/labels_view'
import v_upload_large from '../upload_large'
import Vue from "vue";
import CodeDiff from 'vue-code-diff/dist/vue-code-diff'
import SshPre from 'simple-syntax-highlighter'
import 'simple-syntax-highlighter/dist/sshpre.css'
export default Vue.extend({

    name: 'input_payload_dialog',
    components: {
      labels_view: labels_view,
      CodeDiff: CodeDiff,
      v_upload_large: v_upload_large,
      SshPre: SshPre
    },
    props: ['project_string_id', 'selected_input'],

    mounted() {

    },

    data() {
      return {
        loading: false,
        is_open: false,
        input: undefined
      }
    },
    watch: {
      selected_input: function (newVal, oldVal) {
        if (newVal && oldVal && newVal.id != oldVal.id) {
          this.input = undefined;
          this.fetch_input_payload(newVal);
        }
      }
    },
    filters: {
      pretty: function (value) {
        return JSON.stringify(JSON.parse(value), null, 2);
      }
    },
    methods: {
      close() {
        this.input = undefined;
        this.is_open = false;
      },
      open() {
        this.is_open = true;
      },
      fetch_input_payload: async function (input) {
        try {
          this.loading = true;
          const response = await axios.post(`/api/walrus/v1/project/${this.$props.project_string_id}/input/view/${input.id}`);
          if (response.status === 200) {
            this.input = response.data.input;
            if (this.input.frame_packet_map) {
              this.input.frame_packet_map = JSON.stringify(this.input.frame_packet_map, undefined, 2)
            }
            if (this.input.instance_list) {
              this.input.instance_list = JSON.stringify(this.input.instance_list, undefined, 2)
            }


          }
        } catch (error) {
          console.error(error)
        } finally {
          this.loading = false;
        }
      }
    }
  }
) </script>
