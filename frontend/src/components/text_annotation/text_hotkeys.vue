<template>
<div v-cloak id="hotkeys-text">
<v-layout column>
  <h2> General </h2>

  <p> <kbd>Esc</kbd> Cancel drawing relation / Deactivate instance</p>
  <p> <kbd>S</kbd> Save </p>
  <p> <kbd>G</kbd> + <b>Select</b> Google It (Fast search in Google) </p>
  <p> <kbd>B</kbd> + <b>Click</b> Label all in document (Beta) </p>

  <h2>Selection</h2>

  <p> <kbd>→</kbd> - Next text token </p>
  <p> <kbd>←</kbd> - Previous text token </p>

</v-layout>

</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend({
  name: 'text_hotkeys',
}) 

</script>
