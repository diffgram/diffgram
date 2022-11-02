<template>
  <div
    v-if="selected.length > 0"
    class="attribute-preview"
  >
    <h4>Global attributes applied:</h4>
    <div class="attribute-preview-chips">
      <div
        v-for="(item, index) in selected"
        v-bind:key="`attribute_preview_${index}`"
        class="chip-wrapper"
      >
        <standard_chip
          small
          disabled
          text_color="black"
          color="grey"
          custom_style="font-size: 8px"
          :message="item"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";
import standard_chip from "./standard_chip.vue";

export default Vue.extend({
  components: { 
    standard_chip 
  },
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
      selected: [] as Array<string>
    }
  },
  watch: {
    global_attribute_groups_list(): void {
      this.set_attributes()
    },
    current_instance: {
      deep: true,
      handler(): void {
        this.set_attributes()
      }
    },
  },
  mounted(): void {
    this.set_attributes()
  },
  methods: {
    set_attributes: function(): void {
      if (this.global_attribute_groups_list && this.current_instance && this.current_instance.attribute_groups) {
        const attribute_groups = this.global_attribute_groups_list.map((group: any) => group.id)
        let selected_names = []
  
        attribute_groups.map((group_id: number) => {
          if (this.current_instance.attribute_groups[group_id]) {
            const group_selected_ids = Object.keys(this.current_instance.attribute_groups[group_id]).map(key => parseInt(key))
            const group_attribute_names = group_selected_ids.map(key => {
              if (this.current_instance.attribute_groups[group_id][key]) return this.current_instance.attribute_groups[group_id][key].name
            })
    
            selected_names = [...selected_names, ...group_attribute_names]
          }
        })
  
        this.selected = selected_names    
      }
    }
  }
});
</script>

<style scoped>
.attribute-preview {
  padding: 10px;
}

.attribute-preview-chips {
  display: flex;
  flex-shrink: 0;
  flex-flow: row wrap;
  max-width: 100%;
}

.chip-wrapper {
  margin-right: 10px;
}
</style>

