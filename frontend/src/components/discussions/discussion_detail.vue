<template>
  <div v-cloak class="discussion-detail-container">
    <main_menu>
    </main_menu>
    <view_edit_issue_panel
      :allow_edit_attached_instances="false"
      :show_attachment_links="true"
      :project_string_id="project_string_id ? project_string_id : this.$store.state.project.current.project_string_id"
      :current_issue_id="parseInt(discussion_id, 10)"
      @close_view_edit_panel="go_back"
      ref="view_edit_issue_panel"
    ></view_edit_issue_panel>
  </div>
</template>

<script>
  import Vue from "vue";
  import view_edit_issue_panel from './view_edit_issue_panel'

  export default Vue.extend({
    name: "discussion_detail",
    model: 'current_discussion',
    components:{
      view_edit_issue_panel,
    },
    props:{
      'project_string_id':{
        default: undefined
      },
      'task_template_id':{
        default: undefined
      },
      'discussion_id': {
        type: String
      },
    },
    data:function () {
      return{
      }
    },
    watch: {

    },
    created() {

    },
    computed:{

    },
    methods:{
      go_back: function(){
        if(this.$props.task_template_id){
          this.$router.push(`/job/${this.$props.task_template_id}/discussions`);
        }
        else{
          this.$router.push(`/discussions/?project=${this.$route.query['project']}`);
        }

      }
    }
  })

</script>

<style>
  .discussion-detail-container{
    padding: 2rem;
  }
</style>
