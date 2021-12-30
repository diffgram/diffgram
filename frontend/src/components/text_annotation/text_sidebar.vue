<template>
    <div>
        <div>
            <h3 :style="`width: 300px`">Labels: </h3>
            <ul>
                <li 
                    class="annotation-list"
                    v-for="annotation in annotations"
                    :key="`list_annotation_item_${annotation.id}`"
                    @mouseover="on_annotation_hover(annotation.id)"
                    @mouseout="on_stop_hover"
                >
                    {{ annotation.label.label.name }}
                </li>
            </ul>
        </div>
        <br />
        <div>
            <h3 :style="`width: 300px`">Relations: </h3>
            <ul>
                <li 
                    class="annotation-list"
                    v-for="relation in relations"
                    :key="`list_relation_item_${relation.id}`"
                    @mouseover="on_relation_hover(relation.id)"
                    @mouseout="on_relation_stop_hover"
                >
                    {{ relation.label.label.name }}
                </li>
            </ul>
        </div>
    </div>
</template>

<script>

  import Vue from "vue";

  export default Vue.extend({
      name: 'text_sidebar',
      props: {
          annotations: {
              type: Array,
              default: []
          },
          relations: {
              type: Array,
              default: []
          }
      },
      methods: {
          on_annotation_hover: function(id) {
              this.$emit('on_annotation_hover', id)
          },
          on_stop_hover: function() {
              this.$emit('on_stop_hover')
          },
          on_relation_hover: function(id) {
              this.$emit('on_relation_hover', id)
          },
          on_relation_stop_hover: function() {
              this.$emit('on_relation_stop_hover')
          }
      }
  })

</script>

<style scoped>
.annotation-list:hover {
    text-decoration: underline;
    cursor: pointer;
}
</style>