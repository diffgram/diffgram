<template>

  <v-card    width="25%"
             height="40%"
             style="position: sticky; top: 75px; border: 1px solid #e0e0e0; min-height: 500px"
             class="justify-start mr-6">
    <v-card-title class="d-flex justify-space-between">
      Schemas

      <button_with_menu
        tooltip_message="Create Schema"
        datacy="create_label_schema_btn"
        icon="mdi-plus"
        color="primary"
        ref="menu"
        v-model="menu_open"
      >

        <template slot="content">

          <v-card elevation="0" style="min-width: 500px">
            <v-card-title>Create Schema:</v-card-title>
            <v-card-text>
              <v_error_multiple :error="error"></v_error_multiple>
              <v-text-field data-cy="text-field-schema-name" v-model="new_schema_name"></v-text-field>
            </v-card-text>
            <v-card-actions class="d-flex justify-lg-space-between align-center">
              <v-btn color="primary" small><v-icon>mdi-close</v-icon>Cancel</v-btn>
              <v-btn color="success" data-cy="create_schema_start" small @click="create_schema"><v-icon>mdi-plus</v-icon>Create</v-btn>
            </v-card-actions>
          </v-card>

        </template>

      </button_with_menu>
    </v-card-title>
    <v-card-text>
      <v-list
        dense
        nav
      >
        <v-list-item
          v-for="item in schema_list"
          :key="item.id"
          link
          :data-cy="`schema_item__${item.name}`"
          :class="item.id === selected_schema.id ? 'selected': ''"
        >
          <v-list-item-icon>
            <v-icon :color="item.id === selected_schema.id ? 'secondary': ''">mdi-shape-plus</v-icon>
          </v-list-item-icon>

          <v-list-item-content @click="select_schema(item)"
                               :class="`${item.id === selected_schema.id ? 'secondary--text': ''} d-flex space-between align-center`">
            <v-list-item-title >{{ item.name }}</v-list-item-title>

          </v-list-item-content>

        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script>
import {create_schema} from '../../services/labelServices'
import sillyname from 'sillyname';

export default {
  name: "schema_card_selector",
  props: {
    'project_string_id': {
      default: null,
      required: true
    },
    'schema_list':{

    }
  },
  data: function(){
    return {
      new_schema_name: sillyname().split(" ")[0],
      selected_schema: {},
      menu_open: false,
      error: null,
    }
  },
  methods: {
    select_schema: function(item){
      this.selected_schema = item;
      this.$emit('schema_selected',item)
    },
    create_schema: async function(){
      if(!this.$props.project_string_id){
        this.error = {
          project: 'Provide project_string_id.'
        }
        return
      }
      if(!this.new_schema_name || this.new_schema_name === ''){
        this.error = {
          name: 'Name must not be empty.'
        }
        return
      }
      let [result, error] = await create_schema(this.$props.project_string_id, this.new_schema_name)
      if(error){
        this.error = this.$route_api_errors(error)

      }
      if(result){
        let new_schema = result;
        this.$store.commit('display_snackbar', {
          text: 'Schema created succesfully.',
          color: 'success'
        })
        this.$refs.menu.close_menu();
        this.$emit('schema_created', new_schema)
      }
    }
  }
}
</script>

<style scoped>
  .selected{
    background: #e0e0e0;
  }
</style>
