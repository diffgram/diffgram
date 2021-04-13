<template>

  <v-tooltip :top="top" :bottom="bottom" :right="right" :left="left">

    <template v-slot:activator="{on}">

      <v-chip v-on="on"
              :color=color
              :text-color=text_color
              :loading="loading"
              :disabled="disabled"
              :small="small"
              :style="custom_style"
              @click="$emit('click', $event)"
              >

        <slot name="chip"> </slot>

        <h2> {{message}} </h2>

        <!-- TODO could also have a template here-->

      </v-chip>

    </template>

    {{ tooltip_message }}

    </v-tooltip>

</template>

<script lang="ts">

/*
 *  
 *  EXAMPLE USAGE:
 *
  
<regular_chip
    :message=custom_value_x
    tooltip_message="This is about the custom value x"
    color="primary"
    tooltip_direction="bottom">
</regular_chip>


OPTIONAL inside regular chip

<template slot="chip">
      
</template>



We style style="cursor: default"
because we may not want the @click thing.

 */

import Vue from "vue";

export default Vue.extend( {
  name: 'regular_chip',
  props: {

    'message': {
      default: null
    },
    'tooltip_message': {
      default: null
    },

    'color': {   // chip color
      default: null,
      type: String
    },
    'text_color': {
      default: 'white',  
      type: String
    },

    'tooltip_direction': {      // left, right, bottom, top
      default: "bottom",
      type: String
    },

    'loading': {
      default: false
     },
    'disabled': {
      default: false
     },
     'small': {
      default: false
     },
     // would be nice if this was automatically detected
     'is_clickable': {
      default: false
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

  computed: {

    custom_style() {

        if (this.is_clickable == true) {
          return "cursor: pointer"
        }
        else {
          return "cursor: default"
        }
    }
  },

  created(){
    this[this.tooltip_direction] = true
  }
}

) </script>
