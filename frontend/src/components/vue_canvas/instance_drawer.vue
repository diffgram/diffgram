
<template>
</template>

<script lang="ts">

import Vue from 'vue'

export default Vue.extend({
      // to do rename this
      props: {
        "instance_list" : {
          default: () => ([])
        },
      },
      data: function(){
        return {
          count_instance_in_ctx_paths: 0,
          instance_hover_index: null,
          instance_hover_type: null,
        }
      },
      methods: {
        emit_hover_event: function () {

            if (this.instance_hover_index != this.previous_instance_hover_index) {

              this.previous_instance_hover_index = this.instance_hover_index

              this.$emit('instance_hover_update',
                [this.instance_hover_index, this.instance_hover_type])
            }

        },
        check_null_hover_case: function () {

          if (this.count_instance_in_ctx_paths == 0) {

            if (this.instance_hover_index != null) { // only update on change
              this.instance_hover_index = null   // careful need to reset this here too
              this.instance_hover_type = null
            }
          }
        },
        draw: function (ctx, done) {
          // instance_list is an array of objects that implement the Instance() interface so can guarantee they all
          // have the draw() method.
          let i = 0;
          for(let instance of this.$props.instance_list){
            instance.draw(ctx, done);
            if(instance.is_hovered){
              this.instance_hover_index = i
              this.count_instance_in_ctx_paths +=1;
              this.instance_hover_type = instance.type;
            }
            i +=1;
          }
          this.check_null_hover_case();
          this.emit_hover_event();
          done();

        }
      }
    })

</script>
