<template>
  <div v-cloak>

    <div v-for tag in tag_list_internal>

        <v-layout :data-cy="`${datacy}__select-tag`"
                  :style="style_color(data.item.color_hex)"
                  >
            {{ data.item.name }}
        </v-layout>

    </div>

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
        'tag_list': {
          default: null,
          type: Array
        },
        'view_only': {
          default: false
        },
        'object_id':{
          default: null
        },
        'object_type':{
          default: null
        }
      },

      watch: {

        value: function (item) {
          this.selected = item
        },
        tag_list: function(new_val, old_val){
            this.tag_list_internal = new_val;
        },
        object_id: function (item) {
          this.list_applied_tags_api(this.object_id, this.object_type)
        },
        object_type: function (item) {    // either case could cause change
          this.list_applied_tags_api(this.object_id, this.object_type)
        },


      },
      created() {
        this.selected = this.value

        if (this.object_id){
          this.get_applied_tags_api(this.object_id, this.object_type)
        }

      },
      mounted(){
        if(this.$props.initial_value){
          this.selected = this.$props.initial_value;
        }
      },

      computed: {

      },
      data() {
        return {
          selected: null,
          loading: false,
          tag_list_internal: [],
          list_applied_tags_api_loading: false,
          error: {},
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

            console.log(response)
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
