<template>

  <v-tooltip :top="top" :bottom="bottom" :right="right" :left="left"
             :disabled="!tooltip_message"
             >

    {{ tooltip_message }}
    

    <template v-slot:activator="{ on }">

      <v-icon v-on="on"
              :color=color
              size="icon_size"
              :style="icon_style"
              :large="large"
              >
        {{icon}}
      </v-icon>

    </template>

  </v-tooltip>

</template>

<script lang="ts">

/*
  
<tooltip_icon
    tooltip_message="Help"
    icon="help"
    color="primary">
</tooltip_icon>

 */

import Vue from "vue"; 
export default Vue.extend( {
  name: 'tooltip_icon',
  props: {
    'color': {
      default: null
    },
    /* A color will override icon_style so default to null.
     * Because sometimes use icon_style becuase vuetify seems to only support "named" colors */
    'icon': {
      default: 'mdi-lifebuoy',
      type: String
    },
    'tooltip_message': {
      default: null,
      type: String
    },
    'tooltip_direction': {      // left, right, bottom, top
      default: "bottom",
      type: String
    },
    'icon_size': {
      default: null
    },
    'icon_style': {
      default: null
    },
    // 1) Add :color="null" on component otherwise it overrides the style!
    // 2) using style not color becuase vuetify seems to only support "named" colors

    'large': { // not quite sure how well this works with 'icon_size' may be a conflict
      default: false,
      type: Boolean
    }

  },
  data() {
    return {
      top: false,
      right: false,
      left: false,
      bottom: false
    }
  },
  created(){
    this[this.tooltip_direction] = true
  }
}

) </script>
