<template>
  <v-menu
    top
    v-model="show_menu"
    max-width="500"
    :position-x="x_position"
    :position-y="y_position"
    absolute
    offset-y
    :close-on-click="false"
    :close-on-content-click="false"
  >
    <v-card class="pa-0">
      <v-card-title>
        What are Ghost Objects? 👻
      </v-card-title>
      <v-card-text>
        <!--
        <img src="" width="200px"
             height="220px"> -->
        <h3> Ghost Objects are "Proposals" </h3>
        Instances that may be useful but are not yet confirmed by you.
        <br> <br>

        <h3> Identify a Ghost by the Dashed Lines</h3>
        All ghost objects are showing as dashed lines instead of the normal solid lines.

        <br><br>
        <h3> Give a Ghost a New Life</h3>
        Click or drag the ghost object to promote it to a normal annotation.
        After, Right click "Pause Object" to prevent future ghost frames for that object from showing.
        <br> <br>

        <h3> Safely Ignore Irrelevant Ghosts</h3>
        If a ghost object is not relevant, you can safely ignore it. Ghost objects
        are never saved unless you expressly click them or drag them.
        <br> <br>
        <h3> Banish All Ghosts</h3>
        To hide/show all ghosts press <kbd>G</kbd> or go to More / Settings / Show Ghost Instances

      </v-card-text>
      <v-card-actions>
        <v-btn @click="show_menu = false" data-cy="ghost_instance_ok" small color="primary">Ok</v-btn>
        <v-btn @click="show_menu = false,
               $store.commit('set_user_setting', ['hide_ghost_canvas_available_alert', true])
               "
               small
               data-cy="ghost_instance_dont_show_again"
               color="secondary">Don't Show Again</v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue";

  export default Vue.extend({
      name: 'ghost_canvas_available_alert',
      props: {
        'x_position': {
          default: undefined
        },
        'y_position': {
          default: undefined
        }
      },
      data() {
        return {
          show_menu: false
        }
      },
      methods: {
        show_alert: function () {
          this.show_menu = true;
        }
      }
    }
  )

</script>
