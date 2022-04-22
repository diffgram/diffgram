<template>
  <v-card flat bordered class="my-card bg-white q-pa-md">
    <div class="row items-center no-wrap">
      <div class="col">
        <div class="text-h6">{{ title }}</div>
      </div>

      <div class="col-auto">
        <flowy-drag-handle>
          <q-btn size="sm" color="grey-7" round flat icon="drag_handle" />
        </flowy-drag-handle>
      </div>
    </div>

    <div class="q-py-md" v-html="description"/>
    <q-btn color="primary" class="q-pa-none" no-caps @click="remove()">Remove</q-btn>
  </v-card>
</template>

<script>
import FlowyPlugin from "@hipsjs/flowy-vue";
import "@hipsjs/flowy-vue/dist/lib/flowy-vue.css";
export default {
  name: "action_step_box",
  props: {
    title: {
      required: true
    },
    description:{

    }
  },
  methods: {
    remove: function(){
      this.$emit('remove')
    }
  }
}
</script>

<style scoped>

</style>
