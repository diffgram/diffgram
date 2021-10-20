<template>
  <div>

    <v-row>
      <v-layout column>


        <slot name="back">

        </slot>

        <tooltip_button
          v-if="back_visible"
          tooltip_message="Back"
          :bottom="true"
          :disabled="disabled_back"
          button_message="Back"
          @click="$emit('back')"
          icon="mdi-arrow-left"
          :text_style="true"
          :left="true"
          color="secondary">
        </tooltip_button>

        <div class="text-right pa-2 pr-4">

          <v-btn
            v-if="next_visible"
            :disabled="disabled_next"
            x-large
            @click="$emit('next')"
            color="success">

            Next
          </v-btn>

          <slot name="next">

          </slot>
  
          <tooltip_button
            v-if="skip_visible"
            tooltip_message="Skip, I will do this later"
            :bottom="true"
            :disabled="disabled_skip"
            button_message="Skip"
            @click="$emit('skip')"
            icon="mdi-debug-step-over"
            :text_style="true"
            :left="true"
            color="secondary">
          </tooltip_button>
         
          <slot name="skip">

          </slot>

        </div>
      </v-layout>
    </v-row>

  </div>
</template>

<script lang="ts">

/*
 
 *
 *  EXAMPLE USAGE:
 *

<wizard_navigation
    name="my_name">

   <template name="back">
      // Example of custom back button
    </template>

</ui_schema>

 */

import Vue from "vue";

export default Vue.extend( {
  name: 'wizard_navigation',

  props: {
    'disabled_next': {
        type: Boolean,
        default: false
     },
    'disabled_skip': {
        type: Boolean,
        default: false
     },
    'disabled_back': {
        type: Boolean,
        default: false
     },
    'next_visible': {
        type: Boolean,
        default: true
     },
    'skip_visible': {
        type: Boolean,
        default: true
     },
    'back_visible': {
        type: Boolean,
        default: true
     },

  },
  data() {
    return {
      visible: true
    }
  },
  created(){
   
  },
  mounted(){
  
  },
  beforeDestroy() {
  },
  methods: {
  }
}

) </script>
