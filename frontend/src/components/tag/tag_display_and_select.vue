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
        tooltip_message="Apply Tags"
        icon="mdi-tag"
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
            :apply_upon_selection="true"
            @tag_applied="new_tag_applied($event, object_id, object_type)"
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
  import tag_select from '@/components/tag/tag_select.vue'
  import tag_display from '@/components/tag/tag_display.vue'

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
        'datacy':{
          default: 'tag-display-and-select'
        },
        'object_id':{
          default: null
        },
        'object_type':{
          default: null
        }
      },

      watch: {

      },
      created() {

      },
      mounted(){
      },

      computed: {

      },
      data() {
        return {
        }
      },

      methods: {
         new_tag_applied: function (event, object_id, object_type){
          this.$refs.tag_display_literal.get_applied_tags_api(object_id, object_type)
        }
      }
    }
  )
</script>
