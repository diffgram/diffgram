<template>
    <v-autocomplete
      v-model="selected_schema"
      return-object
      item-value="id"
      item-text="name"
      ref="schema_select"
      class="label_schema_selector"
      data-cy="label_schema_selector"
      :label="label"
      :disabled="schema_list_loading || disabled"
      :items="schema_list"
      :prepend-icon="icon ? 'mdi-shape-plus' : null"
      :filter="on_filter_schemas"
      @focus="on_focus"
      @blur="on_blur"
      @change="on_change_schema"
    />
</template>

<script lang="ts">
import Vue from "vue"
import { get_schemas } from "../../services/labelServices";

export default Vue.extend({
  name: "label_schema_selector",
  props:{
    project_string_id: {
      type: String,
      required: true
    },
    disabled: {
      type: Boolean,
      default: false
    },
    initial_schema: {
      type: Object,
      default: undefined
    },
    label: {
      type: String,
      default: 'Select Schema'
    },
    icon: {
      type: Boolean,
      default: true
    }
  },
  async mounted() {
    await this.fetch_schema_list();

    if(this.initial_schema) {
      this.selected_schema = this.initial_schema;
    }
    else {
      this.selected_schema = this.schema_list[0];
    }

    this.on_change_schema(this.selected_schema)
  },
  data() {
    return {
      schema_list: [] as Array<any>,
      error: null as Object,
      schema_list_loading: false as Boolean,
      selected_schema: {} as Object
    }
  },
  methods: {
    on_focus: function(): void {
      this.$emit('on_focus')
    },
    on_blur: function() :void {
      this.$emit('on_blur')
    },
    on_change_schema: function(schema: any): void {
      this.$emit('change', schema)
      this.$refs.schema_select.blur()
    },
    on_filter_schemas: function(item: Object, query_text: string): string{
      return item["name"].toLocaleLowerCase().includes(query_text.toLocaleLowerCase())
    },
    fetch_schema_list: async function(): Promise<void> {
      this.schema_list_loading = true
      let [result, error] = await get_schemas(this.project_string_id);

      if(error) {
        this.error = this.$route_api_errors(error);
      }

      if(result) {
        this.schema_list = result;
      }

      this.schema_list_loading = false;
    }
  }
})
</script>

<style scoped>
.label_schema_selector {
  max-width: 300px;
}
</style>
