<template>
  <v-container class="create-discussion-container">
    <main_menu>
    </main_menu>
    <v-layout class="d-flex flex-column">
      <v-card-title class="headline d-flex align-center">
        <v-icon size="36" color="primary">mdi-comment-text-multiple</v-icon>
        Create Discussion
      </v-card-title>
      <v-layout class="d-flex column">
<!--        For now no attachments are supported -->
        <v-layout class="d-flex flex-column">
          <v-text-field v-model="current_discussion.title" label="Issue Name"></v-text-field>
<!--          <p class="ma-0"><strong>Attached Instances</strong></p>-->
<!--          <v-container class="d-flex flex-wrap">-->
<!--            <v-chip color="primary" small v-for="instance in selected_instances">-->
<!--              <template>-->
<!--                <span style="font-size: 10px">-->
<!--                    ID: {{instance.id}}-->
<!--                </span>-->
<!--              </template>-->
<!--            </v-chip>-->
<!--          </v-container>-->
        </v-layout>
        <v-layout class="d-flex flex-column">
          <v-layout  class="d-flex justify-end pb-0 pr-4">

            <editor-menu-bar :editor="editor" v-slot="{ commands, isActive }">

              <div class="menubar d-flex justify-end">

                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.bold() }"
                  @click="commands.bold"
                >
                  <v-icon>mdi-format-bold</v-icon>
                </v-btn>

                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.italic() }"
                  @click="commands.italic"
                >
                  <v-icon>mdi-format-italic</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.underline() }"
                  @click="commands.underline"
                >
                  <v-icon name="underline" >mdi-format-underline</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.bullet_list() }"
                  @click="commands.bullet_list"
                >
                  <v-icon name="underline" >mdi-format-list-bulleted</v-icon>
                </v-btn>

                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.strike() }"
                  @click="commands.strike"
                >
                  <v-icon>mdi-format-strikethrough</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.code_block() }"
                  @click="commands.code_block"
                >
                  <v-icon>mdi-xml</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.paragraph() }"
                  @click="commands.paragraph"
                >
                  <v-icon>mdi-format-paragraph</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.heading({ level: 1 }) }"
                  @click="commands.heading({ level: 1 })"
                >
                  <v-icon>mdi-format-header-1</v-icon>
                </v-btn>

                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.heading({ level: 2 }) }"
                  @click="commands.heading({ level: 2 })"
                >
                  <v-icon>mdi-format-header-2</v-icon>
                </v-btn>

                <v-btn
                  class="menubar__button"
                  icon
                  :class="{ 'is-active': isActive.heading({ level: 3 }) }"
                  @click="commands.heading({ level: 3 })"
                >
                  <v-icon>mdi-format-header-3</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button"
                  icon
                  @click="commands.undo"
                >
                  <v-icon>mdi-undo</v-icon>
                </v-btn>

                <v-btn
                  class="menubar__button"
                  icon
                  @click="commands.redo"
                >
                  <v-icon>mdi-redo</v-icon>
                </v-btn>




              </div>
            </editor-menu-bar>


          </v-layout>
          <editor-content :editor="editor" class="discussion-create">

          </editor-content>
        </v-layout>

      </v-layout>

      <v_error_multiple :error="error">
      </v_error_multiple>

      <v_error_multiple :error="create_issue_error">
      </v_error_multiple>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="green darken-1"
          text
          data-cy="start-importing"
          @click="close_issue_panel()"
        >
          Close
        </v-btn>
        <v-btn

          color="green darken-1"
          text
          :loading="loading_create_issue"
          data-cy="start-importing"
          @click="create_discussion"
        >
          Create Discussion
        </v-btn
        >
      </v-card-actions>
    </v-layout>
  </v-container>
</template>

<script>
  import Vue from "vue";
  import axios from '../../services/customInstance';
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
    TodoList,
    Bold,
    Code,
    Image,
    Italic,
    Link,
    Placeholder,
    Strike,
    Underline,
    History,
  } from 'tiptap-extensions'
  export default Vue.extend({
    name: "create_discussion",
    model: 'current_discussion',
    props: {
      'project_string_id': {
        default: undefined
      },
    },
    components: {
      EditorContent,
      EditorMenuBar,
      EditorMenuBubble,
    },
    data: function () {
      return {
        editor: new Editor({
          extensions: [

            new BulletList(),
            new CodeBlock(),
            new HardBreak(),
            new Heading({ levels: [1, 2, 3] }),
            new HorizontalRule(),
            new ListItem(),
            new OrderedList(),
            new TodoItem(),
            new TodoList(),
            new Link(),
            new Bold(),
            new Code(),
            new Image(),
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
            new Blockquote(),
          ],
          content: '',
          onFocus: this.focus_comment_box,
          onBlur: this.focus_out_comment_box,
        }),

        loading_create_issue: false,
        create_issue_error: {},
        selected_instances: [],
        current_discussion: {
          description: '',
          title: '',
          attached_elements: [],
        },
        description: '',
        title: '',
        error: {},
      }
    },
    created() {

    },
    computed: {
      project_string: function(){
        let project_string_id = null;
        if (this.$route.query.project) {
          project_string_id = this.$route.query.project
        }
        else {
          // Fallback to current project if no query param is provided.
          project_string_id = this.$store.state.project.current.project_string_id;
        }
        return project_string_id
      }
    },
    methods: {
      empty_form: function () {
        this.title = '';
        this.description = '';
        this.selected_instances = '';
      },
      go_to_discussion_detail: function(){
        this.$router.push(`/discussion/${this.current_discussion.id}/?project=${this.project_string}`);
      },
      create_discussion: async function () {
        this.loading_create_issue = true;
        try {
          const response = await axios.post(`/api/v1/project/${this.project_string}/issues/new`, {
            title: this.current_discussion.title,
            type: 'discussion',
            marker_frame_number: this.$props.frame_number,
            description: this.editor.getHTML(),
            attached_elements: this.attached_elements
          })
          if (response.status === 200) {
            this.current_discussion = response.data.issue;
            this.$emit('new_issue_created', response.data.issue);
            this.empty_form();
            this.go_to_discussion_detail();

          }
        } catch (error) {
          this.create_issue_error = this.$route_api_errors(error);
          console.error(error);

        } finally {
          this.loading_create_issue = false;
        }
      },
      close_issue_panel: function () {
        this.description = '';
        this.notes = '';
        this.$emit('close_issue_panel')
      }
    }
  })

</script>

<style>
  .discussion-create .ProseMirror{
    border: none;
    outline: none;
    min-height: 285px;
    width: 100%;
    background-color: #fafbfc;
    border: 1px solid #e1e4e8;
    border-radius: 15px;
    padding: 1rem;
  }
  .discussion-create .ProseMirror p{
    margin: 0 !important;
  }
  .discussion-create .ProseMirror.focus-visible.ProseMirror-focused{
    white-space: pre-wrap;
    min-height: 285px;
    width: 100%;
    background-color: #fafbfc;
    border: 2px solid #aabfdc;
    border-radius: 15px;
    box-shadow: #bad1f3;
  }
  .menubar{
    margin-bottom: 5px;
  }
  .create-discussion-container{
    padding: 0 4rem;
    margin-top: 2rem;
  }
</style>
