<template>
  <v-btn-toggle @change="on_toggle_change" v-model="toggle_exclusive" color="secondary" class="mr-2">
    <v-btn  data-cy="1_click_mode_button" class="pa-1 pt-4 pb-4" x-small>

      <v-icon>mdi-cursor-default-click-outline</v-icon>
      <span class="button-text">1 Click</span>
    </v-btn>

    <v-btn   data-cy="guided_mode_button" class="pa-1 pt-4 pb-4" x-small>
      <v-icon>mdi-handshake-outline</v-icon>
      <span class="button-text">Guided</span>
    </v-btn>
  </v-btn-toggle>
</template>

<script>
  import Vue from "vue";

export default Vue.extend({
  name: "guided_1_click_mode_selector",
  props: {

  },
  components: {

  },
  data: function () {
    return {
      toggle_exclusive: 0,
    }
  },
  mounted() {


  },
  beforeDestroy() {

  },

  methods: {
    set_active(num){
      this.toggle_exclusive = num;
    },
    on_toggle_change(){
      if(this.toggle_exclusive === 0){
        this.$emit('mode_set', '1_click')
      }
      else if(this.toggle_exclusive === 1){
        this.$emit('mode_set', 'guided')
      }
    }
  },

  computed: {
  }

})
</script>
<style>
.button-text{
  margin: auto;
  font-size: 0.6rem;
  font-weight: bold;

}
</style>
