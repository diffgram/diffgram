<template>
<div v-cloak id="hotkeys-text">
<v-layout column>
  <h2> General </h2>

  <p> <kbd>Esc</kbd> Cancel drawing rwelation </p>
  <p> <kbd>S</kbd> Save </p>

</v-layout>

</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend({
  name: 'text_hotkeys',
}) 

</script>
