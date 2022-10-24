<template>
    <v-select
      class="instance_type_select"
      label="Instance type"
    />
</template>

<script>
import Vue from "vue"
export default Vue.extend({
    name: "instance_type_select"
})
</script>

<style scoped>
.instance_type_select {
    max-width: 200px;
}
</style>
