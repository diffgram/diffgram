<template>
  <exam_template_detail_admin
    v-if="show_admin_view"
    :exam_id="exam_id"
  >

  </exam_template_detail_admin>
  <exam_template_detail_annotator
    :exam_id="exam_id"
    v-else
  >

  </exam_template_detail_annotator>
</template>

<script lang="ts">

import exam_template_detail_admin from "../exam/exam_template_detail_admin";
import exam_template_detail_annotator from "../exam/exam_template_detail_annotator";
import Vue from "vue";

export default Vue.extend({
  name: "exam_template_detail",
  props: ["exam_id"],
  components: {
    exam_template_detail_admin,
    exam_template_detail_annotator,
  },

  data() {
    return {
      roles: null,
      show_admin_view: false,
    };
  },
  mounted() {
    this.roles = this.$store.getters.get_project_roles(this.$store.state.project.current.project_string_id);
    console.log('AAAA', this.roles)
    if(this.roles && this.roles.length > 0){
      if(this.roles.includes("admin")){
          this.show_admin_view = true
      }
      else{
        this.show_admin_view = false
      }
    }
  },
  computed: {

  },
  methods: {

  },
});
</script>

<style>
.exam-detail-container {
  padding: 0 10rem;
  margin-top: 2rem;
  height: 100%;
}
</style>
