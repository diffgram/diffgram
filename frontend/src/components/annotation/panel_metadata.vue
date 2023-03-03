<template>
  <div class="grey  mr-2 pr-2 pl-2 mb-1">
    <p class="ma-0 pa-0 text--black font-weight-light" style="color: white; font-size: 12px" >
      {{file.ordinal != undefined ? `${file.ordinal}.` : ''}} {{file.original_filename}}
    </p>
  </div>
</template>

<script>
// In your Vue component.
import Vue from 'vue'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
export default Vue.extend({
  name: "panel_metadata",
  components: { Splitpanes, Pane },
  props: {
    file: {type: Object, required: true},
  },
  methods: {

  }
})
</script>

<style scoped>

</style>
