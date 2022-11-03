<template>
  <v-tooltip
    :top="top"
    :bottom="bottom"
    :right="right"
    :left="left"
    :disabled="!tooltip_message"
  >
    <template v-slot:activator="{ on }">
      <v-chip
        v-on="on"
        :color="color"
        :text-color="text_color"
        :loading="loading"
        :disabled="disabled"
        :small="small"
        :style="custom_style"
        :class="is_clickable ? 'clickable' : ''"
        @click="$emit('click', $event)"
      >
        <slot name="chip" />
        <h2>{{ message }}</h2>
      </v-chip>
    </template>
    {{ tooltip_message }}
  </v-tooltip>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({
  name: "standard_chip",
  props: {
    message: {
      type: String,
      required: true,
    },
    tooltip_message: {
      type: String,
      default: null,
    },
    color: {
      type: String,
      default: null,
    },
    text_color: {
      type: String,
      default: "white",
    },
    /**
     * left, right, bottom, top
     */
    tooltip_direction: {
      type: String,
      default: "bottom",
    },
    loading: {
      default: false,
    },
    disabled: {
      default: false,
    },
    small: {
      default: false,
    },
    is_clickable: {
      default: false,
    },
  },
  data() {
    return {
      top: false as Boolean,
      right: false as Boolean,
      left: false as Boolean,
      bottom: false as Boolean,
    };
  },
  created() {
    this[this.tooltip_direction] = true;
  },
});
</script>

<style scoped>
.clickable {
  cursor: pointer;
}
</style>
