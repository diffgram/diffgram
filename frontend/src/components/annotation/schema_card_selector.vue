<template>

  <v-card    width="256"
             height="500"
             style="position: sticky; top: 75px"
             class="justify-start mr-6">
    <v-navigation-drawer>
      <v-list
        dense
        nav
      >
        <v-list-item
          v-for="item in schema_list"
          :key="item.title"
          link
        >
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>

          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
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
  }
}
</script>

<style scoped>

</style>
