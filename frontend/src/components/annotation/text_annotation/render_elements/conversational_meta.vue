<template>
<div class="container">
    <v-avatar
      color="primary"
      size="40"
    >
      <span class="white--text text-h5">{{ username[0] }}</span>
    </v-avatar>
    <p>{{ username }}</p>
    <p>{{ date_time }}</p>
</div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
    name: "conversational_meta",
    props: {
      workign_file: {
        type: Object,
        default: null
      },
      global_attribute_groups_list: {
        type: Array,
        default: null
      },
      annotation_ui_context: {
        type: Object,
        default: null
      },
    },
    computed: {
      username: function() {
        const author_attribute = this.global_attribute_groups_list.find(attr => attr.prompt.toLowerCase() === 'author')
        const author_name = this.annotation_ui_context.instance_store.instance_store[this.workign_file.id].global_instance.attribute_groups[author_attribute.id]
        return author_name
      },
      date_time: function() {
        // console.log("here")
        const time_attribute = this.global_attribute_groups_list.find(attr => attr.prompt.toLowerCase() === 'time')
        const date_attribute = this.global_attribute_groups_list.find(attr => attr.prompt.toLowerCase() === 'date')

        const time = this.annotation_ui_context.instance_store.instance_store[this.workign_file.id].global_instance.attribute_groups[time_attribute.id]

        return time
      },
    }
})
</script>

<style scoped>
p {
  color: grey;
  margin-bottom: 5px
}

.container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

</style>