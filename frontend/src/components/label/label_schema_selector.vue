<template>
  <div>
    <v-autocomplete
      label="Select Schema"
      return-object
      data-cy="label_schema_selector"
      :disabled="schema_list_loading"
      @change="on_change_schema"
      prepend-icon="mdi-group"
      item-value="id"
      item-text="name"
      ref="schema_select"
      class="ma-0"
      :filter="on_filter_schemas"
      @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
      @blur="$store.commit('set_user_is_typing_or_menu_open')"
      :items="schema_list"
      v-model="selected_schema">

    </v-autocomplete>
  </div>
</template>

<script>
import {get_schemas} from "@/services/labelServices";

export default {
  name: "label_schema_selector",
  props:{
    project_string_id:{
      required: true
    },
    initial_schema:{
      default: undefined
    }
  },
  async mounted() {
    await this.fetch_schema_list();
    this.selected_schema = this.initial_schema;
  },
  data:function (){
    return{
      schema_list: [],
      error: null,
      schema_list_loading: false,
      selected_schema: []
    }
  },
  methods:{
    on_change_schema: function(schema){
      this.$emit('change', schema)
    },
    on_filter_schemas: function(item, query_text, item_text){
      return item.name.toLocaleLowerCase().includes(query_text.toLocaleLowerCase())

    },
    fetch_schema_list: async function(){
      this.schema_list_loading = true
      let [result, error] = await get_schemas(this.project_string_id);
      if(error){
        this.error = this.$route_api_errors(error);
        this.schema_list_loading = false;
      }
      if(result){
        this.schema_list = result;
      }
      this.schema_list_loading = false;
    }
  }
}
</script>

<style scoped>

</style>
