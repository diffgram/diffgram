<template>

  <v-card    width="256"
             height="40%"
             style="position: sticky; top: 75px; border: 1px solid #e0e0e0; min-height: 500px"
             class="justify-start mr-6">
    <v-card-title class="d-flex justify-space-between">
      Schemas
      <button_with_menu
        tooltip_message="Create Schema"
        icon="mdi-plus"
        color="primary"
      >

        <template slot="content">

          <v-card>
            <v-card-title>Create Schema:</v-card-title>
            <v-card-text>
              <v-text-field v-model="new_schema_name"></v-text-field>
            </v-card-text>
          </v-card>

        </template>

      </button_with_menu>
    </v-card-title>
    <v-navigation-drawer>
      <v-list
        dense
        nav
      >
        <v-list-item
          v-for="item in schema_list"
          :key="item.title"
          link
          :class="item.id === selected_schema.id ? 'selected': ''"
        >
          <v-list-item-icon>
            <v-icon :color="item.id === selected_schema.id ? 'secondary': ''">mdi-group</v-icon>
          </v-list-item-icon>

          <v-list-item-content @click="select_schema(item)" :class="item.id === selected_schema.id ? 'secondary--text': ''">
            <v-list-item-title >{{ item.name }}</v-list-item-title>
          </v-list-item-content>

        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </v-card>
</template>

<script>
export default {
  name: "schema_card_selector",
  props: {
    'schema_list':{

    }
  },
  data: function(){
    return {
      new_schema_name: '',
      selected_schema: {}
    }
  },
  methods: {
    select_schema: function(item){
      this.selected_schema = item;
      this.$emit('schema_selected',item)
    }
  }
}
</script>

<style scoped>
  .selected{
    background: #e0e0e0;
  }
</style>
