<template>
  <v-menu
    top
    v-model="show_menu"
    max-width="250"
    :position-x="x_position"
    :position-y="y_position"
    absolute
    offset-y
    :close-on-click="false"
    :close-on-content-click="false"
  >
    <v-card class="pa-0">
      <v-card-title>
        <v-icon color="primary" size="30">mdi-polyline</v-icon>
        Polygon Autoborder now Available!
      </v-card-title>
      <v-card-text>
        <img src="https://d9hhrg4mnvzow.cloudfront.net/get.diffgram.com/3137b50c-unnamed-1.gif" width="200px"
             height="220px">
        You can now perform autobordering on a polygon by clicking any of the nodes of polygon when drawing
        and then clicking another point to automatically border the polygon.
      </v-card-text>
      <v-card-actions>
        <v-btn @click="show_menu = false" small color="success" data-cy="ok_autoborder">Ok</v-btn>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue";

  export default Vue.extend({
      name: 'autoborder_avaiable_alert',
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
