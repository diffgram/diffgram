<template>
  <div v-cloak>

    <v-row class="pa-4">

      <div v-for="tag in selected">

          <v-chip
            v-if="tag.name"
            :data-cy="`${datacy}__select-tag`"
            :style="style_color(tag.color_hex)"
            color="white"
                    >
            {{ tag.name | truncate(30) }}
          </v-chip>
      </div>

    </v-row>

    <v_error_multiple :error="error">
    </v_error_multiple>
 
  </div>
</template>


<script lang="ts">

  import Vue from "vue";
  import axios from '../../services/customInstance';

  export default Vue.extend({

      name: 'tag_display',

      props: {
        'value': {   // built in vue js
          default: null
        },
        'project_string_id': {
          type: String
        },
        'datacy':{
          default: 'tag-display'
        },
        'object_id':{
          default: null
        },
        'object_type':{
          default: null
        },
        'tag_display_refresh_trigger':{
          default: null
        }
      },

      watch: {

        value: function (item) {
          this.selected = item
        },
        object_id: function (item) {
          this.get_applied_tags_api(this.object_id, this.object_type)
        },
        object_type: function (item) {    // either case could cause change
          this.get_applied_tags_api(this.object_id, this.object_type)
        },
        tag_display_refresh_trigger: function (item) {    // either case could cause change
          this.get_applied_tags_api(this.object_id, this.object_type)
        },


      },
      created() {
        this.selected = this.value

        if (this.object_id){
          this.get_applied_tags_api(this.object_id, this.object_type)
        }

      },
      mounted(){
      },

      computed: {

      },
      data() {
        return {
          selected: null,
          loading: false,
          selected: [],
          list_applied_tags_api_loading: false,
          error: {},
        }
      },

      filters: {
        truncate: function (value, numchars) {
          return value && value.length > numchars ? value.substring(0, numchars) + "..." : value
          }
      },

      methods: {
        style_color: function (hex) {
          return "color: #" + hex
        },

        get_applied_tags_api(object_id, object_type){
          this.list_applied_tags_api_loading = true
          this.error = {}

          axios.post('/api/v1/project/' + this.$store.state.project.current.project_string_id +
              '/tag/list/applied', {
                'object_id' : object_id,
                'object_type' : object_type

          }).then(response => {

            this.list_applied_tags_api_loading = false

            this.selected = response.data.tag_list

          })
          .catch(error => {
            console.error(error);
            this.$route_api_errors(error)
            this.list_applied_tags_api_loading = false
          });
        }
      }
    }
  )
</script>
