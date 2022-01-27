<template>
  <div class="exam-detail-container">

  </div>
</template>

<script lang="ts">
import axios from "axios";
import * as examsServices from "../../services/examsService"
import Vue from "vue";

export default Vue.extend({
  name: "exam_child_list",
  props: ["exam_id"],
  components: {
  },

  data() {
    return {
      child_exams_list: [],
      loading_children: false,

    }
  },
  created() {

  },
  computed: {},
  beforeDestroy() {

  },
  methods: {
    get_child_exams_list: async function(){
      let project_string = this.$store.project.current.project_string_id;
      this.loading_children = true;
      const child_exams_list = await examsServices.get_child_exams(project_string, this.exam_id);
      this.child_exams_list = child_exams_list;
      this.loading_children = false;
    },
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
