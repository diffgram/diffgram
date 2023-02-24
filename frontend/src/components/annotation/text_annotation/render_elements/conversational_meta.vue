<template>
<div class="container">
    <v-avatar
      v-if="username"
      color="primary"
      size="40"
    >
      <span class="white--text text-h5">{{ username[0] }}</span>
    </v-avatar>
    <br />
    <p>{{ username }}</p>
    <p>{{ time }}</p>
    <p>{{ date }}</p>
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
        const author_attribute = this.global_attribute_groups_list.find(attr => attr.name.toLowerCase() === 'message_author')

        if (this.annotation_ui_context.instance_store.instance_store[this.workign_file.id]) {
          const author_name = this.annotation_ui_context.instance_store.instance_store[this.workign_file.id].global_instance.attribute_groups[author_attribute.id]
          return author_name
        }

        return null
      },
      time: function() {
        const time_attribute = this.global_attribute_groups_list.find(attr => attr.name.toLowerCase() === 'message_time')

        if (this.annotation_ui_context.instance_store.instance_store[this.workign_file.id]) {
          const time = this.annotation_ui_context.instance_store.instance_store[this.workign_file.id].global_instance.attribute_groups[time_attribute.id]
          
          return time
        }

        return null
      },
      date: function() {
        const date_attribute = this.global_attribute_groups_list.find(attr => attr.name.toLowerCase() === 'message_date')

        if (this.annotation_ui_context.instance_store.instance_store[this.workign_file.id]) {
          const date = this.annotation_ui_context.instance_store.instance_store[this.workign_file.id].global_instance.attribute_groups[date_attribute.id]
  
          return date
        }

        return null
      }
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