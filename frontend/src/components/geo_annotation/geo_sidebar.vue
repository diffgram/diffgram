<template>
    <div style="
        width: 350px; 
        border-right: 1px solid grey; 
        max-height: calc(100vh - 100px);
        height: calc(100vh - 100px);
        position: sticky;
        left: 0;
        top: 100px;
        ">
        <h1 style="width: 350px">Sidebar</h1>
    </div>
</template>

<script>
import Vue from "vue"
export default Vue.extend({
    name: "geo_sidebar"
})
</script>