<script setup lang="ts">
// This starter template is using Vue 3 <script setup> SFCs
// Check out https://vuejs.org/api/sfc-script-setup.html#script-setup
import HelloDiffgramEmbed from "./components/HelloDiffgramEmbed.vue";
</script>

<template>
  <div>
    <img
      src="assets/download.png"
      class="logo diffgram"
      alt="Diffgram logo"
    >
  </div>
  <HelloDiffgramEmbed msg="Diffgram Embed"></HelloDiffgramEmbed>
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
