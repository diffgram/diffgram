<template>
<div v-cloak id="hotkeys-text">
<v-layout column>
  <h2> General </h2>

  <p> <kbd>Esc</kbd> Cancel drawing relation </p>
  <p> <kbd>S</kbd> Save </p>
  <p> <kbd>G</kbd> + <b>Select</b> Fast search in Google </p>

</v-layout>

</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend({
  name: 'text_hotkeys',
}) 

</script>
