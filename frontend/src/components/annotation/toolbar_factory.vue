<template>
  <h1>Toolbar</h1>
</template>

<script lang="ts">
import Vue from "vue";
import image_and_video_toolbar from "./image_and_video_annotation/toolbar.vue"

export default Vue.extend({
  name: "toolbar_factory",
  components:{
    image_and_video_toolbar
  },
})
</script>
