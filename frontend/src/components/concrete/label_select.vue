<template>
    <v-select
      class="label_select"
      label="Label"
    />
</template>

<script>
import Vue from "vue"
export default Vue.extend({
    name: "label_select"
})
</script>

<style scoped>
.label_select {
    max-width: 200px;
}
</style>
