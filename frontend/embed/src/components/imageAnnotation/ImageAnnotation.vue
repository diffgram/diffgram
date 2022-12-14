<template>
  <div>
    <h1>Hello diffgram embed :) </h1>
    <img src="https://picsum.photos/600/600">
  </div>
</template>

<script lang="ts">
export default {
  name: "ImageAnnotation",
  props: {
    file: {
      default: null,
    }
  }
}
</script>

<style scoped>

</style>
