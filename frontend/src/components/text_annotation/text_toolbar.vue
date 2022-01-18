<template>
    <v-toolbar
        dense
        width="100%"
        elevation="0"
        fixed
        :height="height"
        style="overflow: hidden; padding: 0; border-bottom: 1px solid #e0e0e0"
    >
        <v-toolbar-items>
            <h1>Text Toolbar</h1>
        </v-toolbar-items>
    </v-toolbar>
</template>

<script>
import Vue from 'vue'
export default Vue.extend({
    name: "text_toolbar"
})
</script>