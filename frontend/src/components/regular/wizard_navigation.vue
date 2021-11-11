<template>
  <div>

    <v-layout>

      <slot name="back">

      </slot>

      <tooltip_button
        v-if="back_visible"
        datacy="wizard_navigation_back"
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

      <v-spacer></v-spacer>

      <div class="text-right pa-2 pr-4">

        <v-btn
          v-if="next_visible"
          :loading="loading_next"
          :disabled="disabled_next"
          x-large
          @click="$emit('next')"
          color="success"
          data-cy="wizard_navigation_next"
               >

          Next
        </v-btn>

        <slot name="next">

        </slot>

        <tooltip_button
          v-if="skip_visible"
          tooltip_message="Skip, I will do this later"
          datacy="wizard_navigation_skip"
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

  </div>
</template>

<script lang="ts">

/*

 *
 *  EXAMPLE USAGE:
 *

<wizard_navigation>

   <template slot="back">
      // Example of custom back button
    </template>

</wizard_navigation>

<wizard_navigation
  @next="go_to_step(3)"   // wizard nav doesn't implement this function just an exmaple
  @skip="go_to_step(3)"
  @back="$emit('back')"
  :disabled_next="label_file_list.length == 0">
</wizard_navigation>

A key assumption here is that we want things like disabled, or skipping back buttons, or renaming etc
to be different on every or nearly every step

So instead of having a single nav on bottom with ever growing complexity of when to enable or disable,
we can have this more simplistic and defined thing for each step

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
    'loading_next':{
      type: Boolean,
      default: false
    }

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
