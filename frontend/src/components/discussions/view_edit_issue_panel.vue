<template>
    <v-card v-if="current_issue"
            class="d-flex flex-column">
      <v_error_multiple :error="update_attachments_error">
      </v_error_multiple>
      <v-progress-circular v-if="loading_get_issue" :indeterminate="true" class="ma-8 align-self-center justify-self-center align-center"></v-progress-circular>
      <v-card-title v-if="!loading_get_issue && current_issue" class="headline">
       <v-container fluid class="pa-0 d-flex align-center">

        <tooltip_button
            tooltip_message="Back To Discussions"
            @click="close_view_edit_panel"
            icon="mdi-arrow-left"
            :icon_style="true"
            :bottom="true"
            color="primary">
        </tooltip_button>

         <span style="font-size: 18px" class="pl-2 font-weight-bold">
              {{current_issue.title}}
         </span>

         <div class="d-flex ml-auto flex-column align-center justify-end">
           <template v-if="current_issue.status === 'open'">
             <span style="font-size: 14px" class="warning--text">Open</span>
             <v-icon color="primary">mdi-lock-open-alert</v-icon>
           </template>
           <template v-if="current_issue.status === 'closed'">
             <span style="font-size: 14px" class="success--text">Closed</span>
             <v-icon color="success">mdi-lock-check</v-icon>
           </template>
         </div>
       </v-container>
        <v-container fluid class="pa-0" v-if="show_attachment_links">
          <v-row class="pa-0">
            <v-col cols="6" class="pa-0 ml-12">
              <p style="font-size: 12px" class="ma-0">Created by {{current_issue.user.first_name}} {{current_issue.user.last_name}}
                at {{current_issue.created_time | moment("LT, ddd, MMMM Do YYYY")}}
                <span v-if="attached_file_id">with attached
                  <span @click="go_to_file(attached_file_id)"
                        class="pa-1 font-weight-bold attachment-link"

                        style="">
                    file {{attached_file_id}}
                  </span>
                </span>
                <span v-if="attached_file_id">&nbsp; and attached
                  <span @click="go_to_task(attached_task_id)"
                        class="pa-1 font-weight-bold attachment-link">
                    task {{attached_task_id}}
                  </span>
                </span>
              </p>
            </v-col>
          </v-row>
        </v-container>
      </v-card-title>
      <v-card-text class="pa-0" v-if="!loading_get_issue">
        <v-container class="d-flex flex-column pa-0 pl-8" fluid>

         <v-row class="d-flex flex-column justify-start pa-0">
          <v-col cols="12" class="pa-0 pt-2 pb-2">

            <tooltip_button
                tooltip_message="Edit Instance Attachments"
                v-if="allow_edit_attached_instances && !attached_instance_edition"
                @click="start_attach_instance_edition"
                icon="attachment"
                :icon_style="true"
                :bottom="true"
                color="primary">
            </tooltip_button>

            <tooltip_button
                tooltip_message="Save Attachments"
                v-if="allow_edit_attached_instances && attached_instance_edition"
                @click="save_attachments"
                :loading="loading_update_attachments"
                icon="mdi-content-save-settings"
                :icon_style="true"
                :bottom="true"
                color="success">
            </tooltip_button>

            <p class="ma-0" v-if="attached_instances.length > 0"><strong>Attached Instances</strong></p>


          </v-col>
         </v-row>
          <v-row class="d-flex flex-wrap" v-if="attached_instances.length > 0">
            <v-col cols="12 pa-0 pb-2">
              <v-chip color="primary" small v-for="instance in attached_instances" >
                <template>
                <span  class="instance-chip" style="font-size: 10px"
                       @click="go_to_instance(instance.instance)">
                    ID: {{instance.instance.id}}
                </span>
                </template>
              </v-chip>
            </v-col>
          </v-row>
          <v-row class="d-flex flex-wrap" v-if="attached_instances.length > 0">
            <v-col cols="12" class="pa-0 pt-2">
              <p class="ma-0" v-if="attached_instances.length > 0"><strong>Related Labels</strong></p>
              <v-chip color="primary" small v-for="label_file in related_labels" >
                <template>
                <span  style="font-size: 10px">
                  <v-icon :style="`color: ${label_file.colour.hex}`">
                    flag
                  </v-icon>
                  {{label_file.label.name}}
                </span>
                </template>
              </v-chip>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>

      <v_error_multiple :error="error">
      </v_error_multiple>


      <div class="pr-2 pt-4" v-if="!loading_get_issue && current_issue">
        <discussion_comments_list
          :project_string_id="project_string_id"
          :discussion_id="current_issue.id"
          :discussion="current_issue"
          ref="comment_list">

        </discussion_comments_list>
        <discussion_comments_new
          :discussion_id="current_issue.id"
          :project_string_id="project_string_id"
          :discussion="current_issue"
          @comment_created="add_comment_to_list"
          @discussion_updated="issue_updated"
        ></discussion_comments_new>

      </div>

    </v-card>

</template>

<script>
  import Vue from "vue";
  import axios from '../../services/customInstance';
  import discussion_comments_new from './discussion_comments_new'
  import discussion_comments_list from './discussion_comments_list'
  import { Editor, EditorContent, EditorMenuBar, EditorMenuBubble, Extension } from 'tiptap';
  import {
    Blockquote,
    CodeBlock,
    HardBreak,
    Heading,
    HorizontalRule,
    OrderedList,
    BulletList,
    ListItem,
    TodoItem,
    Image,
    TodoList,
    Bold,
    Code,
    Italic,
    Link,
    Placeholder,
    Strike,
    Underline,
    History,
  } from 'tiptap-extensions'

  export default Vue.extend({
    name: "view_edit_issue_panel",
    model: 'current_issue',
    components:{
      discussion_comments_new,
      discussion_comments_list,
      EditorContent,
      EditorMenuBar,
      EditorMenuBubble,
    },
    props:{
      'allow_edit_attached_instances': {
        default: true
      },
      'show_attachment_links': {
        default: false,
      },
      'project_string_id':{
        default: undefined
      },
      'task':{
        default: undefined
      },
      'job_id':{
        default: undefined
      },
      'file':{
        default: undefined
      },
      'current_issue_id': {
        type: Number
      },
      'instance_list': {
        default: () => ([])
      }
    },
    data:function () {
      return{
        editor: new Editor({
          extensions: [
            new Blockquote(),
            new BulletList(),
            new CodeBlock(),
            new HardBreak(),
            new Image(),
            new Heading({ levels: [1, 2, 3] }),
            new HorizontalRule(),
            new ListItem(),
            new OrderedList(),
            new TodoItem(),
            new TodoList(),
            new Link(),
            new Bold(),
            new Code(),
            new Italic(),
            new Strike(),
            new Underline(),
            new History(),
            new Placeholder({
              emptyEditorClass: 'is-editor-empty',
              emptyNodeClass: 'is-empty',
              emptyNodeText: 'Write a comment...',
              showOnlyWhenEditable: true,
              showOnlyCurrent: true,
            }),
          ],
          editable: false,

          content: '',
          onFocus: this.focus_comment_box,
          onBlur: this.focus_out_comment_box,
        }),
        attached_instance_edition: false,
        loading_update_attachments: false,
        update_attachments_error: {},
        issue_fetch_error: {},
        loading_get_issue: false,
        selected_instances: [],
        current_issue: undefined,
        description: '',
        title: '',
        error: {},
      }
    },
    watch: {
      instance_list: {
        deep: true,
        immediate: true,
        handler(newvalue, oldvalue) {
          // TODO: Might need to add extra logic for frame number in case of video mode.
          this.selected_instances = newvalue.filter(elm => elm.selected === true);
        }
      },
      current_issue_id: {
        deep: true,
        immediate: true,
        handler(newvalue, oldvalue){
         this.get_issue(newvalue);
          this.attached_instances;
        }
      },
    },
    created() {

    },
    computed:{
      view_mode: function(){
        if(this.$props.current_issue){
          return true;
        }
        return false;
      },
      related_labels: function(){
        const result = [];
        const processed_labels = [];
        for(let i = 0; i < this.attached_instances.length; i++){
          const current = this.attached_instances[i];
          if(!current.instance){
            continue;
          }
          if(!processed_labels.includes(current.instance.label_file.label.name)){
            processed_labels.push(current.instance.label_file.label.name)
            result.push(current.instance.label_file)

          }
        }
        return result
      },
      attached_instances: function(){
        if(!this.current_issue_id){
          return []
        }
        if(!this.current_issue){
          return []
        }

        let attached_instances = this.current_issue.attached_elements.filter(elm => elm.type === 'instance');
        const attached_instances_ids = attached_instances.map(x => x.instance_id);
        // Add the instances from the selected instances in the canvas.
        if(this.instance_list){
          this.instance_list.forEach(instance =>{
            if(instance.selected && !attached_instances_ids.includes(instance.id)){
              attached_instances.push({
                'type': 'instance',
                'instance_id': instance.id
              })
            }
            if(!instance.selected && attached_instances_ids.includes(instance.id)){
              const index = attached_instances.indexOf(instance.id);
              attached_instances.splice(index, 1);
            }
          })
        }
        return attached_instances;
      },
      attached_task_id: function(){
        if(!this.current_issue){
          return
        }
        if(!this.current_issue.attached_elements){
          return
        }
        const elements = this.current_issue.attached_elements;
        const tasks = elements.filter(element => element.type === 'task');
        if(tasks.length === 0){
          return
        }
        return tasks[0].task_id
      },
      attached_file_id: function(){
        if(!this.current_issue){
          return
        }
        if(!this.current_issue.attached_elements){
          return
        }
        const elements = this.current_issue.attached_elements;
        const tasks = elements.filter(element => element.type === 'file');
        if(tasks.length === 0){
          return
        }
        return tasks[0].file_id
      }
    },
    methods:{
      issue_updated(discussion){
        this.current_issue = discussion;
        this.$emit('update_issues_list', discussion)
      },
      start_attach_instance_edition(discussion){
        this.attached_instance_edition = true;
        this.$emit('start_attach_instance_edition', discussion);
      },
      stop_attach_instance_edition(discussion){
        this.attached_instance_edition = false;
        this.$emit('stop_attach_instance_edition', discussion);
      },
      add_comment_to_list(comment){
        this.$refs.comment_list.add_comment(comment);
      },
      async save_attachments(){
        this.loading_update_attachments = true;
        try {
          const result = await axios.post(`/api/v1/project/${this.$props.project_string_id}/discussion/${this.current_issue.id}/update`, {
            attached_elements: this.selected_instances.map(instance => {
              return {
                'type': 'instance',
                'instance_id': instance.id,
              }
            })
          })
          if (result.status === 200) {
            const discussion_updated = result.data.discussion;
            this.current_issue = discussion_updated
            this.$emit('discussion_updated', discussion_updated);
            this.stop_attach_instance_edition();
          }

        } catch (error) {
          this.update_attachments_error = this.$route_api_errors(error)
          console.error(error)

        } finally {
          this.loading_update_attachments = false;

        }
      },
      async get_issue(issue_id){
        if(!issue_id){
          return
        }
        this.loading_get_issue = true;
        try{
          const response = await axios.get(`/api/v1/project/${this.$props.project_string_id}/issues/${issue_id}`)
          if(response.status === 200){
            this.set_attached_instances(response.data.issue);
            this.current_issue = response.data.issue;
            this.editor.setContent(this.current_issue.description);
          }
        }
        catch (error) {
          console.error(error);
          this.issue_fetch_error =  this.$route_api_errors(error);
        }
        finally {
          this.loading_get_issue = false;
        }
      },
      set_attached_instances: function(current_issue){
        if(!current_issue){ return }
        const instances = current_issue.attached_elements.filter(elm => elm.type === 'instance');
        const instances_ids = instances.map(elm => elm.instance_id);
        // Unselect all instances.
        this.$props.instance_list.forEach(elm => {
          elm.selected = false;
        });
        // Select only attached instances.
        this.$props.instance_list.forEach(elm => {
          if(instances_ids.includes(elm.id)){
            elm.selected = true;
          }
        });
        // Set Selected instances
        this.selected_instances = this.$props.instance_list.filter(elm => elm.selected);
        this.$emit('update_canvas')
      },
      go_to_task: function(task_id){
        this.$router.push(`/task/${task_id}`)
      },
      go_to_instance: function(instance){
        // TODO Question - maybe restrict in studio mode, or different approach?
        // because (discussed in the addQueriesToLocation) while in studio we don't want to use router.push()
        this.$router.push(`/file/${this.attached_file_id}/?instance=${instance.instance_id}&frame=${instance.frame_number}`)
      },
      go_to_file: function(file_id){
        this.$router.push(`/file/${file_id}`)
      },
      empty_form: function(){
        this.title = '';
        this.description = '';
        this.attached_elements = '';
        this.selected_instances = '';
      },
      edit_issue: async function(){
        if(!this.current_issue){
          return
        }
        this.loading_create_issue = true;
        try{
          const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/issues/new`, {
            title: this.current_issue.title,
            description: this.current_issue.description,
            attached_elements: this.attached_elements
          })
          if(response.status === 200){
            this.$emit('new_issue_created', response.data.issue);
            this.empty_form();
            this.close_issue_panel();

          }
        }
        catch (error) {

        }
        finally {
          this.loading_create_issue = false;
        }

      },
      close_view_edit_panel: function(){
        if(this.$props.instance_list){
          this.$props.instance_list.forEach(elm => {
            elm.selected = false;
          });
        }

        this.$emit('close_view_edit_panel')
      }
    }
  })

</script>

<style>
  .discussion-view .ProseMirror{
    border: none;
    outline: none;
    width: 100%;
    background-color: #ffffff;
    padding: 1rem;
  }
  .discussion-view .ProseMirror p{
    margin: 0 !important;
  }
  .discussion-view .ProseMirror.focus-visible.ProseMirror-focused{
    white-space: pre-wrap;
    width: 100%;
    background-color: #ffffff;
    border-radius: 15px;
  }
  .menubar{
    margin-bottom: 5px;
  }
</style>
<style scoped>
  .attachment-link{
    color: #0095f1;
    background: #eaf5ff;
    border-radius: 15px
  }
  .attachment-link:hover{
    cursor: pointer;
  }
  .instance-chip:hover{
    cursor: pointer;
  }
</style>
