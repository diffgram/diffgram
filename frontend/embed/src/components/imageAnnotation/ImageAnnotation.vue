<template>
  <div class="d-flex">
    <v-app :theme="true">
      <v-card>
        <v-card-title>What animal is this?</v-card-title>
        <v-btn color="success">Save</v-btn>
        <v-radio-group>
          <v-radio
            :label="`Dog`"
            :value="'dog'"
          ></v-radio>
          <v-radio
            :label="`Cat`"
            :value="'cat'"
          ></v-radio>
          <v-radio
            :label="`Horse`"
            :value="'horse'"
          ></v-radio>
        </v-radio-group>
      </v-card>
      <img src="https://picsum.photos/600/600">
    </v-app>

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
