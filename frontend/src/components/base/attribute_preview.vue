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
    },
    // This prob is not really needed, but due to vue limitation need to have it
    added_attributes: {
      type: Array,
      required: true
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
    added_attributes(): void {
      this.set_attributes()
    },
    current_instance: {
      deep: true,
      handler(newValue, oldValue): void {
        console.log(newValue, oldValue)
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
        const attribute_groups = this.global_attribute_groups_list.map((group: any) => ({group_id: group.id, kind: group.kind}))
        let selected_names = []
  
        attribute_groups.map(({group_id, kind}) => {
          const attribute = this.current_instance.attribute_groups[group_id]
          if (attribute) {
            if (kind === 'tree') {            
              if (attribute) {
                const group_selected_ids = Object.keys(attribute).map(key => parseInt(key))
                const group_attribute_names = group_selected_ids
                  .map(key => { if (attribute[key]) return attribute[key].name})
                  .filter(item => item)
        
                selected_names = [...selected_names, ...group_attribute_names]
              }
            }
            else if (['select', 'radio'].includes(kind)) selected_names = [...selected_names, attribute.display_name]
            else if (kind === 'multiple_select') attribute.map(option => selected_names.push(option.display_name))
            else if (['text', 'slider', 'time', 'date'].includes(kind)) selected_names.push(`${attribute}`)
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

