<template>
  <div v-cloak>

    <v-combobox
              :items="tag_list_internal"
              v-model="selected"
              :label="label"
              :data-cy="datacy"
              :search-input.sync="search"
              item-value="id"
              :multiple="true"
              :disabled="loading || view_only"
              @input="$emit('input', $event)"
              @change="$emit('change', $event); user_change_event()"
              @focus="$emit('focus', $event); $store.commit('set_user_is_typing_or_menu_open', true)"
              @blur="$store.commit('set_user_is_typing_or_menu_open')"
              :filter="on_filter"
              :clearable="clearable"
              return-object
    >

      <template v-slot:item="data">

        <v-layout :data-cy="`${datacy}__select-tag`"
                  :style="style_color(data.item.color_hex)"
                  >
            {{ data.item.name }}
        </v-layout>

      </template>

      <template v-slot:selection="data">
        <v-chip :style="style_color(data.item.color_hex)">
          <template>

            <v-layout :data-cy="`${datacy}__select-tag`">
                {{ data.item.name }}
            </v-layout>

          </template>
        </v-chip>

      </template>

      <template slot="no-data">
        <v-list-item v-if="allow_new_creation">
          <v-list-item-content>
            <v-list-item-title>
              Press <kbd>enter</kbd> to create. <strong>{{ search }}</strong>
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>

        <v-list-item v-if="!allow_new_creation">
          <v-list-item-content>
            <v-list-item-title>
               No results found.
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </template>

    </v-combobox>

    <v_error_multiple :error="error">
    </v_error_multiple>
  

  </div>
</template>

<!--

Example usage

<tag_select
    v-model="tag"
    :tag_list="$store.state.project.current.tag_list">
</tag_select>

Where is a dict in data() eg  tag: {}

-->

<script lang="ts">

  import Vue from "vue";
  import axios from '../../services/customInstance';

  export default Vue.extend({

      name: 'tag_select',

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
        'initial_value': {
          default: undefined,
        },
        'label': {
          default: 'Apply or Create Tags'
        },
        'datacy':{
          default: 'tag-select'
        },
        'dataset':{
          default: null
        },
        'object_id':{
          default: null
        },
        'object_type':{
          default: null
        },
        'modify_upon_selection':{
          default: false
        },
        'allow_new_creation':{  // e.g. search context
          default: true
        },
        'clearable':{  
          default: false
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

        if (!this.$props.tag_list){
          this.tag_list_api()
        }

        if (this.object_id){
          this.list_applied_tags_api(this.object_id, this.object_type)
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
          search: null,
          tag_list_api_loading: false,
          apply_tag_api_loading: false,
          new_tag_api_loading: false,
          error: {},
          previous_tag_list_selected: []
        }
      },

      methods: {
        on_filter: function(item, query_text, item_text){
          return item.name.toLocaleLowerCase().includes(query_text.toLocaleLowerCase())

        },
        style_color: function (hex) {
          return "color: #" + hex
        },

        tag_list_api() {

          this.tag_list_api_loading = true
          this.error = {}

          axios.get('/api/v1/project/' + this.$store.state.project.current.project_string_id +
              '/tags/list', {

          }).then(response => {

            if (response.data['tag_list'] != null) {

              this.tag_list_internal = response.data['tag_list']
            }

            this.tag_list_api_loading = false

          })
            .catch(error => {
              console.error(error);
              this.$route_api_errors(error)
              this.tag_list_api_loading = false
            });
        },

        remove_applied_tag_api(tag_id, object_id, object_type) {

 
          if (this.$props.modify_upon_selection == false) { return }

          this.remove_tag_api_loading = true
          this.error = {}

          axios.post('/api/v1/project/' + this.$store.state.project.current.project_string_id +
              '/tag/applied/remove', {
                'tag_id' : tag_id,
                'object_id' : object_id,
                'object_type' : object_type

          }).then(response => {

            this.remove_tag_api_loading = false

            this.$emit('tag_prior_applied_removed')

          })
            .catch(error => {
              console.error(error);
              this.$route_api_errors(error)
              this.remove_tag_api_loading = false
            });
        },



        apply_tag_api(tag_name, object_id, object_type) {

          if (this.$props.modify_upon_selection == false) { return }

          this.apply_tag_api_loading = true
          this.error = {}

          axios.post('/api/v1/project/' + this.$store.state.project.current.project_string_id +
              '/tag/apply', {
                'tag_name' : tag_name,
                'object_id' : object_id,
                'object_type' : object_type

          }).then(response => {

            this.apply_tag_api_loading = false

            this.$emit('tag_applied')

          })
            .catch(error => {
              console.error(error);
              this.$route_api_errors(error)
              this.apply_tag_api_loading = false
            });
        },

        async apply_tag(changed_tag){
          let tag_object = undefined
          if (typeof changed_tag === 'string' || changed_tag instanceof String) {
            tag_object = await this.new_tag_api(changed_tag)
            console.log(tag_object)
          } else {
            tag_object = changed_tag
          }
          if (tag_object) {
            // object
            this.apply_tag_api(
                tag_object.name,
                this.$props.object_id,
                this.$props.object_type
            )
          }

        },

        async remove_applied_tag(changed_tag){
          let tag_object = await this.remove_applied_tag_api(
            changed_tag.id, this.object_id, this.object_type)
        },

        async user_change_event(){
          // Difference between newly selected and new to overall system
          let changed_tag = this.get_changed_tag()

          let user_wants_to_apply_tag = true
          let user_wants_to_remove_applied_tag = false

          if (this.previous_tag_list_selected.length >
              this.selected.length) {
            user_wants_to_remove_applied_tag = true
            user_wants_to_apply_tag = false
          }

          this.previous_tag_list_selected = this.selected.slice()
          if (!changed_tag) { return }

          if (user_wants_to_apply_tag){
            this.apply_tag(changed_tag)
          }

          if (user_wants_to_remove_applied_tag){
            this.remove_applied_tag(changed_tag)
          }


        },

        list_applied_tags_api(object_id, object_type){
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
        },

        get_changed_tag(){
          // because veutify returns list with all elements

          console.log(this.previous_tag_list_selected)

          if (this.previous_tag_list_selected.length >
              this.tag_list_internal.length) {
            for (let previous_tag of this.previous_tag_list_selected){
              let removed_tag = this.selected.find(x => x.id == previous_tag.id)
              if (removed_tag) {
                return removed_tag
              }
            }
          } else {
            let most_recent = this.selected.at(-1)
            return most_recent
          }

        },

        async new_tag_api(name) {

          if (this.allow_new_creation == false) {
            this.remove_string_from_internal(name)
            return
          }

          let already_exists = this.tag_list_internal.find(x => x.name == name)
          if (already_exists) {
            return already_exists
          }

          this.new_tag_api_loading = true
          this.error = {}

          return await axios.post('/api/v1/project/' + this.$store.state.project.current.project_string_id +
              '/tag/new', {
            'name': name
          }).then(response => {
            
            this.new_tag_api_loading = false

            this.tag_list_internal.push(response.data.tag)
            this.previous_tag_list_selected.push(response.data.tag) 
            this.selected.push(response.data.tag)
            this.remove_string_from_internal(response.data.tag.name)

            this.$emit('new_tag_created')

            return response.data.tag

          })
            .catch(error => {
              console.error(error);
              this.$route_api_errors(error)
              this.new_tag_api_loading = false
            });
        },

        remove_string_from_internal(name){
          let index = this.selected.indexOf(name);
          console.log(index)
          if (index > -1) {
            this.selected.splice(index, 1);
          }
          console.log(this.selected)
        }



      }
    }
  )
</script>
