<template>
  <div class="d-flex">
    <h1>Hello diffgram embed :) </h1>
    <v-card>
      <v-card-title>What animal is this?</v-card-title>
      <v-radio-group>
        <v-radio
          :label="`Dog`"
          :value="n"
        ></v-radio>
        <v-radio
          :label="`Cat`"
          :value="n"
        ></v-radio>
        <v-radio
          :label="`Horse`"
          :value="n"
        ></v-radio>
      </v-radio-group>
    </v-card>
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
