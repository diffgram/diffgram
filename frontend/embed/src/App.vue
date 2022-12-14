<script setup lang="ts">
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://vuejs.org/api/sfc-script-setup.html#script-setup
import HelloDiffgramEmbed from "./examples/HelloDiffgramEmbed.vue";
</script>

<template>
  <div>
    <div>
      <img
        src="./assets/download.png"
        class="logo diffgram"
        alt="Diffgram logo"
      >
    </div>
    <h1 style="text-align: left; margin-bottom: 4rem">
      Example #1: Embedded Image Annotation
    </h1>
    <HelloDiffgramEmbed msg="Diffgram Embed"></HelloDiffgramEmbed>
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.diffgram:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
