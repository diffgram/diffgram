<template>
    <v-select
      class="label_schema_select"
      label="Select Schema"
      prepend-inner-icon="mdi-shape-plus"
    />
</template>

<script>
import Vue from "vue"
export default Vue.extend({
    name: "label_schema_select"
})
</script>

<style scoped>
.label_schema_select {
    max-width: 300px;
}
</style>
