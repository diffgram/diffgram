<template>

  <div @mouseover="mouseover"
       @mouseleave="mouseleave"
       v-if="visible"
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
      visible: true
    }
  },
  created(){
    this.refresh_state_from_ui_schema()
  },
  mounted(){
    this.show_ui_schema_refresh = this.$store.watch((state) => {
        return this.$store.state.ui_schema.refresh
      },
      (new_val, old_val) => {
        this.refresh_state_from_ui_schema()
      },
    )
  },
  beforeDestroy() {
    this.show_ui_schema_refresh()
  },
  methods: {
    refresh_state_from_ui_schema(){
      if (this.$props.name == undefined) { return true } 
      this.visible = this.$store.getters.get_ui_schema(this.$props.name, 'visible')
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
