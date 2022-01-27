<template>
  <div class="exam-detail-container">
    <v-list>
      <v-list-item
        v-if="child_exams_list.length > 0"
        v-for="item in child_exams_list"
        :key="item.id"
      >
        <v-list-item-icon>
          <v-icon
            v-if="item.icon"
            color="pink"
          >
            mdi-star
          </v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title v-text="item.name"></v-list-item-title>
        </v-list-item-content>

        <v-list-item-avatar>
          <v-img :src="item.avatar"></v-img>
        </v-list-item-avatar>
      </v-list-item>
    </v-list>
    <v-card fluid class="d-flex flex-column justify-center align-center ma-4" elevation="2" style="min-height: 500px">
      <h1>No Examinations Yet</h1>
      <v-icon size="128">mdi-archive</v-icon>
    </v-card>
  </div>
</template>

<script lang="ts">
import axios from "axios";
import {get_child_exams} from "../../services/examsService"
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
      const child_exams_list = await get_child_exams(project_string, this.exam_id);
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
