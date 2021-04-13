<template>
</template>

<script lang="ts">
  import Vue from 'vue'

  export default Vue.extend({

      props: ["ord", "message", "x", "y"],

      methods: {
        draw: function (ctx, done) {

          var canvas = ctx.canvas;

          ctx.textAlign = "center";
          ctx.fillStyle = "black";
          ctx.font = "bold 30pt Courier";
          ctx.fillText(this.message, parseInt(this.x), parseInt(this.y));
          
          done();

        }
      }

    })


</script>
