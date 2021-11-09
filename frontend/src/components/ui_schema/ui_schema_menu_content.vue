<template>
<div v-cloak>

  <v-layout class="d-flex flex-column"
            v-if="get_target_element() === 'instance_selector'">
    <v-list-item
      link
      @click="hide"
      data-cy="hide_target_element"
    >

      <v-list-item-icon>
        <tooltip_icon
          tooltip_message="Hide"
          icon="mdi-eye-off"
          color="primary"
        />
      </v-list-item-icon>
      <v-list-item-content>
        <v-list-item-title class="pr-4">
          Hide {{get_target_element()}}
        </v-list-item-title>

      </v-list-item-content>
    </v-list-item>
    <v-divider></v-divider>
    <h4 class="mt-3 ml-2">Allowed Types: </h4>

    <instance_type_multiple_select
      :instance_type_list="instance_type_list"
      :multiple="true"
      :initial_value="initial_selected_types()"
      :init_all_selected="initial_selected_types() ? false : true"
      @input="on_change_instance_select($event)"
    >

    </instance_type_multiple_select>
  </v-layout>

  <v-layout v-else>
    <v-list-item
      link
      @click="hide"
      data-cy="hide_target_element"
    >

      <v-list-item-icon>
        <tooltip_icon
          tooltip_message="Hide"
          icon="mdi-eye-off"
          color="primary"
        />
      </v-list-item-icon>
      <v-list-item-content>
        <v-list-item-title class="pr-4">
          Hide {{get_target_element()}}
        </v-list-item-title>
      </v-list-item-content>
    </v-list-item>
  </v-layout>




</div>

</template>

<script lang="ts">

  import Vue from 'vue';
  import axios from 'axios';
  import {UI_Schema} from './ui_schema'
  import instance_type_multiple_select from './../annotation/instance_type_multiple_select'

  export default Vue.extend({
    name: 'ui_schema_menu_content',
    components: {
      instance_type_multiple_select
    },
    props: {

    },
    data() {
      // move context menu off the page out of view when hidden
      return {
        instance_type_list: [
          {'name': 'polygon',
            'display_name': 'Polygon',
            'icon': 'mdi-vector-polygon'
          },
          {'name': 'box',
            'display_name': 'Box',
            'icon': 'mdi-checkbox-blank'
          },
          {'name': 'tag',
            'display_name': 'Tag',
            'icon': 'mdi-tag'
          },
          {'name': 'point',
            'display_name': 'Point',
            'icon': 'mdi-circle-slice-8'
          },
          {'name': 'line',
            'display_name': 'Fixed Line',
            'icon': 'mdi-minus'
          },
          {'name': 'cuboid',
            'display_name': 'Cuboid 2D',
            'icon': 'mdi-cube-outline'
          },
          {'name': 'ellipse',
            'display_name': 'Ellipse & Circle',   // feel free to change if circle is it's own thing with update
            'icon': 'mdi-ellipse-outline'
          },
          {'name': 'curve',
            'display_name': 'Curve Quadratic',
            'icon': 'mdi-chart-bell-curve-cumulative'
          }
        ],
      }
    },

    computed: {

    },

    watch: {

    },
    created() {
    },
    mounted() {

    },
    beforeDestroy() {

    },
    methods: {
      hide: function(){
        this.$emit('hide');
      },
      get_target_element: function () {
        // careful target is stored on ui_schema generally not `current`
        return this.$store.state.ui_schema.target_element
      },
      initial_selected_types: function(){
        if(!this.get_ui_schema()){
          return []
        }
        if(!this.get_ui_schema().instance_selector){
          return []
        }
        if(!this.get_ui_schema().instance_selector.allowed_instance_types){
          return []
        }
        return this.get_ui_schema().instance_selector.allowed_instance_types
      },
      get_ui_schema: function () {
        if (this.$store.state.ui_schema.current == undefined) {
          throw new Error("this.$store.state.ui_schema.current is undefined")
        }
        return this.$store.state.ui_schema.current
      },

      on_change_instance_select: function(new_type_list){
        this.$store.commit('set_ui_schema_element_value',
          ['instance_selector', 'allowed_instance_types', new_type_list])
        this.$store.commit('set_ui_schema_element_value',
          ['instance_selector','visible', true])
      }
    }

  });
</script>

<style>
  .context-menu {
    position: absolute;
    margin: 0;
    box-sizing: border-box;
    display: none;
    z-index: 10000;
  }

  .save-menu {
    position: absolute;
    margin: 0;
    box-sizing: border-box;
    display: none;
    z-index: 1000;
  }

  .context-menu.visible {
    display: block;
  }
  .save-menu.visible {
    display: block;
  }
</style>
