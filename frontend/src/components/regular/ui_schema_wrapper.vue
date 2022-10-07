<template>
  <div 
    v-if="visible"
    @mouseover="mouseover"
  >
    <slot />
  </div>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend( {
  name: 'ui_schema',
  props: {
    'name': {
        type: String,
        required: true
     }
  },
  data() {
    return {
      visible: true as Boolean
    }
  },
  created(){
    this.refresh_state_from_ui_schema()
  },
  beforeDestroy() {
    this.show_ui_schema_refresh()
  },
  methods: {
    show_ui_schema_refresh(): void {
      this.show_ui_schema_refresh = this.$store.watch(
        () => this.$store.state.ui_schema.refresh,
        this.refresh_state_from_ui_schema()
      )
    },
    refresh_state_from_ui_schema(): void {
      this.visible = this.$store.getters.get_ui_schema(this.$props.name, 'visible')
    },
    mouseover(event: Event): void {
      this.$store.commit('set_ui_schema_event', [this.name, event])
    }
  }
}

) </script>
