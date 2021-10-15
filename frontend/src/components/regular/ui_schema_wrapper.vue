<template>

  <div @mouseover="mouseover"
       @mouseleave="mouseleave"
       v-if="show()"
       >

    <slot>

    </slot>

  </div>
</template>

<script lang="ts">

/*
 
 *
 *  EXAMPLE USAGE:
 *

<ui_schema
    name="my_name">

   <template>
      <v-layout>


      </v-layout>
    </template>

</ui_schema>

 */

import Vue from "vue";

export default Vue.extend( {
  name: 'ui_schema',
  props: {
    'name': {
        type: String,
        default: undefined
     }
  },
  data() {
    return {

    }
  },
  created(){

  },
  methods: {
    show(){
      if (this.$props.name == undefined) { return true } 
      return this.$store.getters.get_ui_schema(this.$props.name, 'visible')
    },
    mouseover(event) {
      this.$store.commit('set_ui_schema_event', [this.name, event])
    },
    mouseleave(event) {
      //this.$store.commit('clear_ui_schema_event')
    }
  }
}

) </script>
