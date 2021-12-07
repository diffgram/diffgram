<template>
  <div v-cloak>
    <v-layout>

      <v-select :items="member_list_internal"
                v-model="item_internal"
                :label="label"
                :data-cy="datacy"
                item-value="member_id"
                :multiple="multiple"
                :disabled="loading || view_only"
                @input="$emit('input', $event)"
                @change="$emit('change', $event)"
                clearable
      >
        <!-- Why >>>>  :item-value="null"  Because for multiple select otherwise
              it doesnt' track selected properly-->
        <!-- Add a tile with Select All as Lalbel and binded on a method that add or remove all items -->
        <template v-slot:prepend-item>
          <v-list-item
            ripple
            :data-cy="`${datacy}__select-all`"
            @click="toggle"
            v-if="allow_all_option"
          >
            <v-list-item-action>
              <v-icon :color="item_internal.length > 0 ? 'indigo darken-4' : ''">
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

          <v-layout :data-cy="`${datacy}__select-user`">
            <v_user_icon v-if="data.item.show_icon" class="mr-4" :user="data.item" :size="25"
                         :font-size="'12px !important'">
            </v_user_icon>
            {{ data.item.first_name}} {{ data.item.last_name}}
          </v-layout>
        </template>

        <template v-slot:selection="{item, index}">
          <v-chip color="primary" small v-if="item.show_icon && index === 0 && !all_selected" >
            <template>
              <v_user_icon :user="item"  class="mr-2" :size="25"
                           :font-size="'12px !important'">
              </v_user_icon>
              <span  style="font-size: 10px">
                <template v-if="show_names_on_selected && index === 0"> {{ item.first_name}} {{ item.last_name}}</template>

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

<!--

Example usage

<member_select
    v-model="member"
    :member_list="$store.state.project.current.member_list">
</member_select>

Where is a dict in data() eg  member: {}

-->

<script lang="ts">

  import axios from 'axios';
  import Vue from "vue";

  export default Vue.extend({

      name: 'member_select',

      props: {
        'value': {   // built in vue js
          default: null
        },
        'project_string_id': {
          type: String
        },
        'kind': {
          default: 'human',
          type: String
        },
        'multiple': {
          default: false,
          type: Boolean
        },
        'member_list': {
          default: null,
          type: Array
        },
        'view_only': {
          default: false
        },
        'allow_all_option': {
          default: false
        },
        'show_names_on_selected': {
          default: true,
        },
        'init_all_selected':{
          default: true,
        },
        'initial_value': {
          default: undefined,
        },
        'label': {
          default: 'Select Members'
        },
        'datacy':{
          default: 'member-select'
        }
      },

      watch: {

        value: function (item) {
          this.item_internal = item
        },

      },
      created() {
        this.item_internal = this.value
      },
      mounted(){
        if(this.$props.initial_value){
          this.item_internal = this.$props.initial_value;
        }
        if(this.$props.init_all_selected){
          this.item_internal = this.member_list_internal.map(memb => memb.member_id);
        }
      },

      computed: {
        all_selected: function(){
          return this.item_internal.length === this.member_list_internal.length;
        },
        one_selected: function(){
          return this.item_internal.length > 0;
        },
        member_list_internal: function () {
          let members = this.$props.member_list.filter(member =>
            member.member_kind == this.$props.kind
          )
          members = members.map(e => ({...e, show_icon: true}))
          return members

        },
        icon () {
          if (this.all_selected) return 'mdi-close-box'
          if (this.one_selected) return 'mdi-minus-box'
          return 'mdi-checkbox-blank-outline'
        },
      },
      data() {
        return {
          item_internal: null,
          loading: false
        }
      },

      methods: {
        toggle () {
          this.$nextTick(() => {
            if (this.all_selected) {
              this.item_internal = []
            } else {
              this.item_internal = this.member_list_internal.slice()
            }
          })
        }

      }
    }
  )
</script>
