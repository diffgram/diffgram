<template>
<div v-cloak id="hotkeys-3d">
<v-layout column>
  <h2> 3D/Sensor Fusion Hotkeys</h2>

  <p> <kbd>T</kbd> Change Transform tool when instance selected (Translate, Rotate, Scale) </p>

  <p> <kbd>X</kbd> Center Camera </p>
  <p> <kbd>WASD</kbd> Move </p>

  <h2> General </h2>

  Right click an instance to bring up context menu.

  <p> <kbd>Esc</kbd> Toggle draw and edit mode </p>

  <p> <kbd>Esc</kbd> (Twice) Cancel current drawing and return to draw mode </p>
  <p> <kbd>Double Click</kbd> Deselect selected instance </p>

  <p> <kbd>W</kbd> Toggle Label Menu </p>
  <p> <kbd>H</kbd> Hide/Show All Instances in File. </p>
  <p> <kbd>Shift + T</kbd>Remove/Add Instance Transparency </p>
  <p> <kbd>G</kbd> Toggle Ghost Instances </p>
  <p> <kbd>1 - 9</kbd> Change label </p>

  <p> <kbd>Shift</kbd> + <kbd>←</kbd>,<kbd>→</kbd> Previous or Next File </p>
  <p> <kbd>Ctrl</kbd> + <kbd>c</kbd> Copy Selected Instance </p>
  <p> <kbd>Ctrl</kbd> + <kbd>v</kbd> Paste Selected Instance </p>

  <p> <kbd>+</kbd> Scale Up Edit Controls </p>
  <p> <kbd>-</kbd> Scale Down Edit Controls </p>

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
