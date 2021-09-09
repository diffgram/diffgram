<template>
<div v-cloak>
<v-layout column>
  <h1>Video Editor Hotkeys</h1>
  <h2> General </h2>

  Right click an instance to bring up context menu.

  <p> <kbd>Esc</kbd> Toggle draw and edit mode </p>

  <p> <kbd>Esc</kbd> (Twice) Cancel current drawing and return to draw mode </p>

  <p> <kbd>W</kbd> Toggle Label Menu </p>
  <p> <kbd>H</kbd> Hide/Show All Instances in File. </p>
  <p> <kbd>Shift + T</kbd>Remove/Add Instance Transparency </p>
  <p> <kbd>G</kbd> Toggle Ghost Instances </p>
  <p> <kbd>1 - 9</kbd> Change label </p>

  <p> <kbd>Shift</kbd> + <kbd>←</kbd>,<kbd>→</kbd> Previous or Next File </p>
  <p> <kbd>Ctrl</kbd> + <kbd>c</kbd> Copy Selected Instance </p>
  <p> <kbd>Ctrl</kbd> + <kbd>v</kbd> Paste Selected Instance </p>

  <p> <kbd>C</kbd> Complete. Save, Mark as Complete, Go to Next.</p>

</v-layout>

</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {

  name: 'hotkeys_sensor_fusion',
  components: {
  },
  props: {

  },
  data() {
    return {

    }
  },
  watch: {

  },
  mounted() {
  },
  computed: {

  },
  methods: {

  }
}

) </script>
