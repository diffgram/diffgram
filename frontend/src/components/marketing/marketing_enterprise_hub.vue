<template>
<div >

<iframe
  src="https://get.diffgram.com/enterprise/hub"
  style="
    position: fixed;
    top: 50px;
    bottom: 100px;
    right: 0px;
    width: 100%;
    border: none;
    margin: 0;
    padding: 0;
    overflow: auto;
    z-index: 0;
    height: 100%;
  ">
</iframe>

</div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend( {
  name: 'enterprise_hub',

  components: {
  },

  data () {
    return {

    }
  }
}
) </script>

