<template>
  <exam_template_detail_admin
    v-if="show_admin_view"
    :exam_id="exam_id"
    :exam="exam"
  >

  </exam_template_detail_admin>
  <exam_template_detail_annotator
    :exam_id="exam_id"
    :exam="exam"
    v-else
  >

  </exam_template_detail_annotator>
</template>

<script lang="ts">

import exam_template_detail_admin from "../exam/exam_template_detail_admin";
import exam_template_detail_annotator from "../exam/exam_template_detail_annotator";
import {get_task_template_details} from '../../services/taskTemplateService'
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
      exam: {},
      show_admin_view: false,
    };
  },
  async mounted() {
    this.roles = this.$store.getters.get_project_roles(this.$store.state.project.current.project_string_id);
    this.exam = await get_task_template_details(this.exam_id);
    if(this.roles && this.roles.length > 0){
      if(this.roles.includes("admin")){
          this.show_admin_view = true
      }
      else{
        this.show_admin_view = false
      }
    }
    let user_id = this.$store.state.user.current.id;
    if(this.exam.member_list_ids.includes("all") || this.exam.member_list_ids.includes(user_id)){
      this.show_admin_view = true
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
