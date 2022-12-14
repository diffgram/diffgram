<script lang="ts">
import {DiffgramUI, DiffgramUIBase} from "../types/annotation/DiffgramUI";
import {onMounted} from "vue";
export default {
  data: function (){
    return{
      diffgramUI: undefined,
      test: 'This is an embedded Annotation UI: '
    }
  },
  async mounted() {
    this.diffgramUI = await DiffgramUI({
      domIDSelector: '#myUI',
      width: 800,
      height: 800
    })

  }
}
</script>

<template>
  <div>
    <h3>{{ test }}</h3>
    <div id="myUI" />
  </div>
</template>

<style scoped>

</style>
