<template>
  <v-container fluid elevation="2" style="min-height: 500px" class="exam-child-list pa-6">
    <v-list     v-if="child_exams_list.length > 0">

        <template
          v-for="(item, index) in child_exams_list"

        >

          <v-list-item :key="item.id" >
            <v-list-item-avatar>
              <v-list-item-avatar class="ma-4">
                <v-img
                  v-if="item.member.profile_image_thumb_url"
                  :alt="`${item.name} avatar`"
                  :src="item.member.profile_image_thumb_url"
                ></v-img>
                <v-icon v-else size="48">
                  mdi-account-circle
                </v-icon>
              </v-list-item-avatar>
            </v-list-item-avatar>

            <v-list-item-title v-text="`Results for ${item.member.first_name} ${item.member.last_name}`">


            </v-list-item-title>
            <v-list-item-subtitle v-text="`${item.member.email}`"></v-list-item-subtitle>

            <v-list-item-action class="mr-10">
              <v-btn color="secondary" @click="go_to_examination(item.id)"><v-icon>mdi-badge</v-icon>Grade</v-btn>
            </v-list-item-action>


          </v-list-item>

          <v-divider v-if="index < child_exams_list.length - 1"></v-divider>
        </template>


    </v-list>
    <v-card v-else fluid class="d-flex flex-column justify-center align-center ma-4" elevation="2" style="min-height: 500px">
      <h1>No Examinations Yet</h1>
      <v-icon size="128">mdi-archive</v-icon>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import {get_examinations} from "../../services/examsService"
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
  async created() {
    await this.get_child_exams_list();
  },
  computed: {},
  beforeDestroy() {

  },
  methods: {
    go_to_examination: function(examination_id){
      let project_string = this.$store.state.project.current.project_string_id;
      this.$router.push(`/${project_string}/examination/${examination_id}`)
    },
    get_child_exams_list: async function(){
      let project_string = this.$store.state.project.current.project_string_id;
      this.loading_children = true;
      const child_exams_list = await get_examinations(project_string,
        this.exam_id,
        this.$store.getters.get_current_mode
      );
      this.child_exams_list = child_exams_list;
      // Populate Member
      for(let examination of this.child_exams_list){
        if(examination.member_list_ids && examination.member_list_ids.length > 0){
          let member_id = examination.member_list_ids[0];
          let member = this.$store.state.project.current.member_list.find(member => member.id === member_id)
          examination.member = member
        }


      }
      this.loading_children = false;
    },
  },
});
</script>

<style>
.exam-child-list {
  height: 100%;
  min-height: 500px;
  border: 1px solid #e0e0e0;
}
</style>
