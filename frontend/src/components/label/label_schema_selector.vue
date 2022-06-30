<template>
  <div>
    <v-autocomplete
      :label="label"
      return-object

      data-cy="label_schema_selector"
      :disabled="schema_list_loading || disabled"
      @change="on_change_schema"
      prepend-icon="mdi-shape-plus"
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
import { get_schemas } from "@/services/labelServices";

export default {
  name: "label_schema_selector",
  props:{
    project_string_id:{
      required: true
    },
    disabled: {
      type: Boolean,
      default: false
    },
    initial_schema:{
      default: undefined
    },
    label: {
      default: 'Select Schema'
    }
  },
  async mounted() {
    await this.fetch_schema_list();
    if(this.initial_schema){
      this.selected_schema = this.initial_schema;
    }
    else{
      this.selected_schema = this.schema_list[0];
    }
    this.on_change_schema(this.selected_schema)
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
      this.$emit('change', schema);
      document.activeElement.blur()
      this.$refs.schema_select.blur()
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
