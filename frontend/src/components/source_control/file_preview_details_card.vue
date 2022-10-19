<template>
  <v-card
    v-if="file"
    :style="`position: absolute; z-index: 9999; width:${file_preview_width}px; height: 70px`"
    height="100"
    width="100"
    class="mx-auto fade-box"
  >
    <v-card-subtitle class="white--text">
      <div class="d-flex flex-row">
        <div class="flex-grow-1">
          <p class="mb-0"><strong>Name:</strong> {{file.original_filename}}</p>
          <p class="mt-0" v-if="file.type === 'compound'"><strong>Attached Assets:</strong> {{child_files.length}}</p>
        </div>
        <v-chip color="secondary" x-small>{{file.type}}</v-chip>
      </div>
    </v-card-subtitle>

  </v-card>
</template>

<script>
export default {
  name: "file_preview_details_card",
  props: {
    'file_preview_width': {
      default: 440
    },
    'file_preview_height': {
      default: 325
    },
    'file': {
      default: null
    },
    'child_files': {
      default: () => ([])
    }
  }
}
</script>

<style scoped>

</style>
