<template>
  <div class="attribute-preview">
    <div
      v-for="(item, index) in selected"
      v-bind:key="`attribute_preview_${index}`"
      class="chip-wrapper"
    >
      <standard_chip
        text_color="grey"
        :message="item"
        :small="true"
      />
    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import standard_chip from "./standard_chip.vue";

export default Vue.extend({
  components: { standard_chip },
  name: "attribute_preview",
  props: {
    global_attribute_groups_list: {
      type: Array,
      default: []
    },
    current_instance: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      selected: []
    }
  },
  mounted() {
    const attribute_groups = this.global_attribute_groups_list.map((group: any) => group.id)
    let selected_names = []

    attribute_groups.map((group_id: number) => {
      const group_selected_ids = Object.keys(this.current_instance.attribute_groups[group_id]).map(key => parseInt(key))
      const group_attribute_names = group_selected_ids.map(key => this.current_instance.attribute_groups[group_id][key].name)

      selected_names = [...selected_names, ...group_attribute_names]
    })

    this.selected = selected_names
  }
});
</script>

<style scoped>
.attribute-preview {
  display: flex;
  flex-shrink: 0;
  flex-flow: row wrap;
  padding: 10px;
  max-width: 100%;
}

.chip-wrapper {
  margin-right: 10px;
}
</style>

