<template>
  <div v-cloak>
    <v-layout>

      <v-select :items="instance_type_list_internal"
                v-model="item_internal"
                :label="label"
                :multiple="multiple"
                item-text="display_name"
                item-value="name"
                :disabled="loading || view_only"
                @input="$emit('input', $event)"
                @change="$emit('change', $event)"
                clearable
      >
        <template v-slot:prepend-item>
          <v-list-item
            ripple
            @click="toggle"
          >
            <v-list-item-action>
              <v-icon v-if="item_internal != undefined" :color="item_internal.length > 0 ? 'indigo darken-4' : ''">
                {{ icon }}
              </v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>
                Select All
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-divider class="mt-2"></v-divider>
        </template>

        <template v-slot:item="data">

          <v-layout>
            <v-icon>{{data.item.icon}}</v-icon>
            {{ data.item.display_name}}
          </v-layout>
        </template>

        <template v-slot:selection="{item, index}">
          <v-chip color="primary" small v-if="item.show_icon && index === 0 && !all_selected" >
            <template>
              <span  style="font-size: 10px">
                <template> {{ item.display_name}} {{ item.last_name}}</template>

              </span>

            </template>
          </v-chip>
          <span v-if="index === 1 && !all_selected" style="font-size: 10px"> (+{{ item_internal.length - 1 }} others)</span>

          <div v-if="all_selected && index === 0" >
            <v-icon color="primary"
                    left >
              mdi-select-all
            </v-icon>
            All
          </div>


        </template>

      </v-select>
    </v-layout>

  </div>
</template>


<script lang="ts">
  import Vue from "vue";

  export default Vue.extend({

      name: 'instance_type_multiple_select',

      props: {
        'value': {   // built in vue js
          default: null
        },
        'kind': {
          default: 'human',
          type: String
        },
        'multiple': {
          default: false,
          type: Boolean
        },
        'instance_type_list': {
          default: null,
          type: Array
        },
        'view_only': {
          default: false
        },
        'allow_all_option': {
          default: false
        },
        'init_all_selected':{
          default: true,
        },
        'initial_value': {
          default: undefined,
        },
        'label': {
          default: 'Allowed Instances: '
        }
      },

      watch: {

        value: function (item) {
          this.item_internal = item
        }

      },
      created() {
        this.item_internal = this.value
      },
      mounted(){
        if(this.$props.initial_value){
          this.item_internal = this.$props.initial_value;
        }
        if(this.$props.init_all_selected){
          this.item_internal = this.instance_type_list_internal.map(elm => elm.name);
        }
      },

      computed: {
        all_selected: function(){
          return this.item_internal.length === this.instance_type_list_internal.length;
        },
        one_selected: function(){
          return this.item_internal.length > 0;
        },
        instance_type_list_internal: function () {
          let instance_type_list = this.$props.instance_type_list.map(e => ({...e, show_icon: true}))
          return instance_type_list

        },
        icon () {
          if (this.all_selected) return 'mdi-close-box'
          if (this.one_selected) return 'mdi-minus-box'
          return 'mdi-checkbox-blank-outline'
        },
      },
      data() {
        return {
          item_internal: [],
          loading: false,
        }
      },

      methods: {
        toggle () {
          this.$nextTick(() => {
            if (this.all_selected) {
              this.item_internal = []
            } else {
              this.item_internal = this.instance_type_list_internal.slice()
            }
          })
        }

      }
    }
  )
</script>
