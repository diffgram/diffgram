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
    v-else-if="!show_admin_view && show_exam"
  >
  </exam_template_detail_annotator>
  <v-container v-else-if="!show_admin_view && !show_exam" class="d-flex justify-center align-center">
    <h2>You don't have credentials for this exam.</h2>
    <no_credentials_dialog ref="no_credentials_dialog" :missing_credentials="missing_credentials"></no_credentials_dialog>
  </v-container>
</template>

<script lang="ts">
import {user_has_credentials} from '../../services/userServices'
import exam_template_detail_admin from "../exam/exam_template_detail_admin";
import no_credentials_dialog from "../task/job/no_credentials_dialog";
import exam_template_detail_annotator from "../exam/exam_template_detail_annotator";
import {get_task_template_details} from '../../services/taskTemplateService'
import Vue from "vue";

export default Vue.extend({
  name: "exam_template_detail",
  props: ["exam_id"],
  components: {
    exam_template_detail_admin,
    no_credentials_dialog,
    exam_template_detail_annotator,
  },

  data() {
    return {
      roles: null,
      exam: {},
      show_admin_view: false,
      missing_credentials: [],
      show_exam: false,
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
    await this.check_credentials();
    this.show_exam = this.has_credentials_or_admin();
    if(!this.show_exam){
      this.show_missing_credentials_dialog()
    }
  },
  computed: {

  },
  methods: {
    has_credentials_or_admin: function(){
      let project_string_id = this.$store.state.project.current.project_string_id;
      if( this.$store.state.user.current.is_super_admin){
        return true
      }
      if(this.user_has_credentials){
        return true
      }
      let roles = this.$store.getters.get_project_roles(project_string_id);
      if(roles && roles.includes('admin')){
        return true
      }
      return false
    },
    show_missing_credentials_dialog: function(){
      if(this.$refs.no_credentials_dialog){
        this.$refs.no_credentials_dialog.open()
      }
    },
    check_credentials: async function(){
      let project_string_id = this.$store.state.project.current.project_string_id;
      let user_id = this.$store.state.user.current.id;
      let [result, error] = await user_has_credentials(
        project_string_id,
        user_id,
        this.exam_id,

      )
      if(error){
        this.error = this.$route_api_errors(error)
        return
      }
      if(result){
        this.user_has_credentials = result.has_credentials;
        this.missing_credentials = result.missing_credentials;
      }
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
