<template>
<div v-cloak>
<v-layout column>

  <h2> General </h2>

  Right click an instance to bring up context menu.

  <p> <kbd>Esc</kbd> Toggle draw and edit mode </p>

  <p> <kbd>Esc</kbd> (Twice) Cancel current drawing and return to draw mode </p>

  <p> <kbd>W</kbd> Toggle Label Menu </p>
  <p> <kbd>H</kbd> Hide/Show All Instances in File. </p>
  <p> <kbd>Shift + T</kbd>Remove/Add Instance Transparency </p>
  <p> <kbd>Shift + R</kbd>Start Review Carrousel </p>
  <p> <kbd>G</kbd> Toggle Ghost Instances </p>
  <p> <kbd>1 - 9</kbd> Change label </p>

  <p> <kbd>Shift</kbd> + <kbd>←</kbd>,<kbd>→</kbd> Previous or Next File </p>

  <h2> Instance </h2>
  <p> <kbd>F</kbd> Snap to Hovered Instance / Unsnap </p>
  <p> <kbd>Ctrl</kbd> + <kbd>c</kbd> Copy Selected Instance </p>
  <p> <kbd>Ctrl</kbd> + <kbd>v</kbd> Paste Selected Instance </p>

  <p> <kbd>C</kbd> Complete. Save, Mark as Complete, Go to Next.</p>

  <h2> Video </h2>

  <p> <kbd>Spacebar</kbd> Play/Pause Video </p>

  <p> <kbd>←</kbd>,<kbd>→</kbd> or <kbd>A</kbd>, <kbd>D</kbd> Previous or Next Frame</p>

  <p> <kbd>N</kbd> New Sequence </p>
  <p> <kbd>Shift</kbd> + <kbd>n</kbd> Jump to Next Instance </p>
  <h2> Image / Frame </h2>
  <p> <kbd>S</kbd> Save </p>

  <p> <kbd>Delete</kbd> Deletes selected instances </p>

  <p> <kbd>Mouse wheel</kbd> Zoom / pan </p>

  <p> <kbd>Z</kbd> Pan Only </p>

  <h2> Keypoints:  </h2>
  <p> <kbd>O</kbd> Show/Hide Occluded Nodes  </p>
  <p>On Guided Mode: <b>Hold</b> <kbd>n</kbd> to draw a node as occluded.  </p>

  <h2> Polygons </h2>
  <p> <kbd>Enter</kbd> Complete polygon (Or click first point again)  </p>

  <p> <b>Hold </b> <kbd>Shift</kbd>
    🔥 Turbo mode, auto places point as you move mouse.
    <br />
    Can switch between this mode and normal as needed by
    releasing shift.</p>

  <h2>Annotation show</h2>
  <p><kbd>→</kbd> - Next instance</p>
  <p><kbd>Space</kbd> - Stop annotation show</p>

</v-layout>

</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {

  name: 'hotkeys',
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
