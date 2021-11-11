<template>
  <div>

    <!-- Disabled flag is in case there isn't a project ... -->

    <v-menu :disabled="!$store.state.project.current || !$store.state.project.current.project_string_id"
            v-model="action_menu"
            :nudge-width="100"
            offset-y
            >

      <template v-slot:activator="{ on }">
        <v-btn v-on="on"
               color="primary"
               text
               :disabled="!$store.state.project.current.project_string_id">
          <v-icon left> mdi-auto-fix </v-icon>
          Action
        </v-btn>
      </template>

      <v-card elevation="4">


        <v-layout column>

          <v-flex v-if=" $store.state.builder_or_trainer.mode == 'builder'">

            <new_flow
      :project_string_id="$store.state.project.current.project_string_id">

            </new_flow>

          </v-flex>

          <v-flex>

            <v-btn color="primary"
                   text
                   @click="route_my_flow_list">
              <v-icon left>mdi-playlist-check</v-icon>
              My Flows
            </v-btn>

          </v-flex>

          <!--
          <v-divider> </v-divider>

          <v-flex>
            <v-btn :disabled="!$store.state.project.current.project_string_id"
                    color="primary"
                    text
                    @click="route_brain_new">
              <v-icon left>add</v-icon>
              New Brain
            </v-btn>
          </v-flex>

          <v-flex>
            <v-btn :disabled="!$store.state.project.current.project_string_id"
                    color="primary"
                    text
                    @click="route_brain_list">
              <v-icon left>mdi-brain</v-icon>
              My brains
            </v-btn>
          </v-flex>
          -->


        </v-layout>
      </v-card>
    </v-menu>
  </div>

</template>

<script lang="ts">

import new_flow from '../action/action_new_flow.vue'

import Vue from "vue"; export default Vue.extend( {
  name: 'main_menu_action',

  components: {
    new_flow : new_flow
  },

  data() {
    return {

      action_menu: false

    }
  },
  computed: {

  },
  methods: {
    route_my_flow_list() {
      this.$router.push("/project/" +
        this.$store.state.project.current.project_string_id
        + "/flow/list")
    },


    route_brain_new() {
      this.$router.push("/project/" + this.$store.state.project.current.project_string_id
        + "/brain/new")
    },
    route_brain_list() {
      this.$router.push("/project/" + this.$store.state.project.current.project_string_id
        + "/brain/home")
    }

  }
}
) </script>
