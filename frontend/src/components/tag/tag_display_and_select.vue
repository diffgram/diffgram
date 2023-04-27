<template>
  <div v-cloak>
    <v-layout>
      <tag_display
        ref="tag_display_literal"
        :object_id="object_id"
        :object_type="object_type"
      >
      </tag_display>

      <button_with_menu
        tooltip_message="Apply or Create Tags"
        icon="mdi-tag"
        :disabled="!show_for_user_role"
        :small="true"
        color="primary"
        :close_by_button="true"
        offset="x"
        menu_direction="left"
        :commit_menu_status="true">

        <template slot="content">

          <tag_select
            :project_string_id="project_string_id"
            :object_id="object_id"
            :object_type="object_type"
            :modify_upon_selection="true"
            @tag_applied="get_applied_tags_api($event, object_id, object_type)"
            @tag_prior_applied_removed="get_applied_tags_api($event, object_id, object_type)"
          >
          </tag_select>

        </template>

      </button_with_menu>
    </v-layout>


  </div>
</template>


<script lang="ts">

import Vue from "vue";
import axios from '../../services/customInstance';
import tag_select from './tag_select.vue'
import tag_display from './tag_display.vue'

export default Vue.extend({

    name: 'tag_display_and_select',

    components: {
      tag_select,
      tag_display
    },

    props: {
      'value': {   // built in vue js
        default: null
      },
      'project_string_id': {
        type: String
      },
      'datacy': {
        default: 'tag-display-and-select'
      },
      'object_id': {
        default: null
      },
      'object_type': {
        default: null
      }
    },

    watch: {},
    created() {

    },
    mounted() {
    },

    computed: {
      show_for_user_role: function(){
        if(!this.$store.state.user){
          return false
        }
        if(!this.$store.state.user.current){
          return false
        }
        if(this.$store.state.user.current.is_super_admin){
          return true
        }
        const member_id = this.$store.state.user.current.member_id
        const result = this.$store.getters.member_in_roles(member_id, ['admin', 'editor'])
        return result
      },
    },
    data() {
      return {}
    },

    methods: {
      get_applied_tags_api: function (event, object_id, object_type) {
        if (this.$refs.tag_display_literal) {
          this.$refs.tag_display_literal.get_applied_tags_api(object_id, object_type)
        }
      }
    }
  }
)
</script>
