<template>
  <button_with_menu
    :menu_open="is_open"
    tooltip_message="Set Node Drawing Order"
    icon="mdi-sort-bool-descending"
    color="primary"
    :x-small="true"
    :close_by_button="true"
    ref="menu"
  >

    <template slot="content">
      <v-card elevation="0" width="400px">
        <v-card-title>
          Node Drawing Order
          <v-spacer></v-spacer>
          <v-btn @click="trigger_save" color="success" small> <v-icon>mdi-content-save</v-icon>Save</v-btn>
        </v-card-title>
        <v-card-text style="border: 1px solid #e0e0e0">
          <v-list>
            <draggable v-model="items">
              <transition-group >
                <v-list-item  v-for="(element, index) in items" :key="index" style="border-bottom: 1px solid #e0e0e0">
                  <v-list-item-avatar :color="element.color ? element.color.hex : 'primary'">
                    <span class="white--text">{{ index+1 }}</span>
                  </v-list-item-avatar>
                  <v-list-item-title><h3 class="font-weight-light">{{element.name}}</h3></v-list-item-title>
                  <v-divider v-if="index < nodes.length - 1" :key="index"></v-divider>
                </v-list-item>
              </transition-group>
            </draggable>
          </v-list>

        </v-card-text>
      </v-card>
    </template>
  </button_with_menu>
</template>

<script>
  import Vue from "vue";
  import draggable from 'vuedraggable'
export default Vue.extend({
  name: "node_order_picker",

  props: {
    nodes: {
      default: [],

    },
    show_order_editor: {
      default: true
    }
  },
  components: {
    draggable
  },
  data: function () {
    return {
      toggle_exclusive: 0,
      is_open: false,
      items: [],
    }
  },
  watch: {
    nodes: function(new_val, old_val){
      this.items = new_val;
    }
  },
  mounted() {
    this.items = this.nodes;

  },
  beforeDestroy() {

  },

  methods: {
    trigger_save: function(){
      for(let i = 0; i < this.items.length; i++){
        this.items[i].ordinal = i + 1;
      }
      this.$emit('order_updated', this.items)
      this.$refs.menu.close_menu();
    },
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
