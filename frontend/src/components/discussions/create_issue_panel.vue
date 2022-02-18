<template>
  <div id="create_issue_panel">
  <v-container max-width="750px">
    <v-card>
      <v-card-title class="headline d-flex align-center">
        <v-icon size="36" color="warning">mdi-alert</v-icon>
        Create Issue
      </v-card-title>
      <v-card-text>
        <v-container class="d-flex flex-column">

          <v-text-field
                v-model="current_issue.title"
                label="Issue Name"
                @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                        >
          </v-text-field>

          <p class="ma-0"><strong>Attached Instances</strong></p>
          <v-container class="d-flex flex-wrap">
            <v-chip color="primary" small v-for="instance in selected_instances">
              <template>
                <span style="font-size: 10px">
                    ID: {{instance.id}}
                </span>
              </template>
            </v-chip>
          </v-container>
        </v-container>
        <v-container>
          <v-container  class="d-flex justify-end pb-0 pr-4">

            <editor-menu-bar :editor="editor" v-slot="{ commands, isActive }">

              <div class="menubar d-flex justify-end flex-wrap">

                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.bold() }"
                  @click="commands.bold"
                >
                  <v-icon size="18">mdi-format-bold</v-icon>
                </v-btn>

                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.italic() }"
                  @click="commands.italic"
                >
                  <v-icon size="18">mdi-format-italic</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.underline() }"
                  @click="commands.underline"
                >
                  <v-icon size="18" name="underline" >mdi-format-underline</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.bullet_list() }"
                  @click="commands.bullet_list"
                >
                  <v-icon size="18" name="underline" >mdi-format-list-bulleted</v-icon>
                </v-btn>

                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.strike() }"
                  @click="commands.strike"
                >
                  <v-icon size="18">mdi-format-strikethrough</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.code_block() }"
                  @click="commands.code_block"
                >
                  <v-icon size="18">mdi-xml</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.paragraph() }"
                  @click="commands.paragraph"
                >
                  <v-icon size="18">mdi-format-paragraph</v-icon>
                </v-btn>
                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.heading({ level: 1 }) }"
                  @click="commands.heading({ level: 1 })"
                >
                  <v-icon size="18">mdi-format-header-1</v-icon>
                </v-btn>

                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.heading({ level: 2 }) }"
                  @click="commands.heading({ level: 2 })"
                >
                  <v-icon size="18">mdi-format-header-2</v-icon>
                </v-btn>

                <v-btn
                  class="menubar__button pa-0"
                  style="width: 20px"
                  icon
                  :class="{ 'is-active': isActive.heading({ level: 3 }) }"
                  @click="commands.heading({ level: 3 })"
                >
                  <v-icon size="18">mdi-format-header-3</v-icon>
                </v-btn>


              </div>
            </editor-menu-bar>


          </v-container>
          <editor-content :editor="editor"
                          class="discussion-create">

          </editor-content>
        </v-container>

      </v-card-text>

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
          @click="create_issue"
        >
          Create Issue
        </v-btn
        >
      </v-card-actions>
    </v-card>
  </v-container>
  </div>
</template>

<script>
  import Vue from "vue";
  import axios from '../../services/customAxiosInstance';
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
    Italic,
    Link,
    Placeholder,
    Strike,
    Underline,
    History, Image,
  } from 'tiptap-extensions'
  export default Vue.extend({
    name: "create_issue_panel",
    model: 'current_issue',
    props: {
      'project_string_id': {
        default: undefined
      },
      'frame_number': {
        default: undefined
      },
      'mouse_position':{
        default: undefined,
      },
      'task': {
        default: undefined
      },
      'job_id': {
        default: undefined
      },
      'file': {
        default: undefined
      },
      'instance_list': {
        default: () => ([])
      }
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
            new Blockquote(),
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
            new Image(),
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
          content: '',
          onFocus({ editor, event }) {
            let context = document.querySelector('#create_issue_panel').__vue__
            context.$store.commit('set_user_is_typing_or_menu_open', true)
          },
          onBlur({ editor, event }) {
            let context = document.querySelector('#create_issue_panel').__vue__
            context.$store.commit('set_user_is_typing_or_menu_open', false)
          },
        }),

        loading_create_issue: false,
        create_issue_error: {},
        selected_instances: [],
        current_issue: {
          description: '',
          title: '',
          attached_elements: [],
        },
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
          this.selected_instances = newvalue.filter(elm => elm.selected === true);
        }
      },
    },
    created() {

    },
    computed: {
      view_mode: function () {
        if (this.$props.current_issue) {
          return true;
        }
        return false;
      },
      attached_elements() {
        // Might include other elements in the future (Maybe sequences? )
        const instances = this.instance_list.filter(elm => elm.selected === true);
        const result = instances.map(elm => ({...elm, type: 'instance'}))
        // Add the file, task and job (If Available)
        if (this.$props.task && this.$props.task.id) {
          result.push({id: this.$props.task.id, 'type': 'task'});
          result.push({id: this.$props.task.file.id, 'type': 'file'});
          result.push({id: this.$props.task.job_id, 'type': 'job'});

        } else if (this.$props.file) {
          result.push({id: this.$props.file.id, 'type': 'file'});
        }
        this.current_issue.attached_elements = result;
        return result;
      }
    },
    methods: {
      empty_form: function () {
        this.title = '';
        this.description = '';
        this.selected_instances = '';
      },
      create_issue: async function () {
        this.loading_create_issue = true;
        try {
          const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/issues/new`, {
            title: this.current_issue.title,
            marker_frame_number: this.$props.frame_number,
            marker_type: 'point',
            marker_data: {
              x: this.$props.mouse_position ? this.$props.mouse_position.x : undefined,
              y: this.$props.mouse_position ? this.$props.mouse_position.y : undefined,
            },
            description: this.editor.getHTML(),
            attached_elements: this.attached_elements
          })
          if (response.status === 200) {
            this.$emit('new_issue_created', response.data.issue);
            this.empty_form();
            this.close_issue_panel();
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
    min-height: 150px;
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
    min-height: 150px;
    width: 100%;
    background-color: #fafbfc;
    border: 1px solid #0366d6;
    border-radius: 15px;
    box-shadow: #bad1f3;
  }
  .menubar{
    margin-bottom: 5px;
  }
</style>
