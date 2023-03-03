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
        default: undefined
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
  mounted(){
    this.show_ui_schema_refresh = this.$store.watch(
      () => this.$store.state.ui_schema.refresh,
      () => {
        this.refresh_state_from_ui_schema()
      },
    )
  },
  beforeDestroy() {
    this.show_ui_schema_refresh()
  },
  methods: {
    refresh_state_from_ui_schema(){
      if (this.$props.name == undefined) return true 
      this.visible = this.$store.getters.get_ui_schema(this.$props.name, 'visible')
    },
    mouseover(event: Event) {
      this.$store.commit('set_ui_schema_event', [this.name, event])
    }
  }
}

) 
</script>