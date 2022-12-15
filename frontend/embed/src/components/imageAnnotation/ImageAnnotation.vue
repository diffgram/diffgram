<template>
  <v-card elevation="4" style="border: 1px solid #e0e0e0" >
    <v-card-title>
      <div class="d-flex justify-space-between">
        <h4> What animal is this?</h4>
        <v-btn color="green">Save</v-btn>
      </div>
    </v-card-title>
    <v-card-text>
      <div class="d-flex">
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
        <img src="https://picsum.photos/600/600">
      </div>
    </v-card-text>
  </v-card>
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
