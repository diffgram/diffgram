<template>
  <v-progress-circular indeterminate color="primary" v-if="loading_comments"
                       class="ma-auto d-flex"></v-progress-circular>
  <v-container class="d-flex justify-end pa-0" fluid v-else>
    <v_error_multiple :error="list_comments_error">
    </v_error_multiple>

    <v-timeline
      dense
      clipped
      class="pa-0"
      style="width: 100%"
    >


      <v-slide-x-transition
        group
      >
        <v-timeline-item
          v-if="discussion"
          :key="`discussion_${discussion_id}`"
          small
        >
          <template v-slot:icon>
            <div v-if="discussion && discussion.user && discussion.user.profile_image_thumb_url" class="mr-1">
              <v-avatar :size="35">
                <img :src="discussion.user.profile_image_thumb_url"/>
              </v-avatar>
            </div>
            <div v-else class="mr-1" style="overflow: visible; width: 50px">
              <v-icon color="white" size="45">account_circle</v-icon>
            </div>
          </template>
          <v-card>
            <v-card-title class="d-flex align-center pa-1" v-if="discussion && discussion.user">

              <span v-if="discussion.user" style="font-size: 12px;">
                <strong>{{discussion.user.first_name}} &nbsp; </strong>
                </span>
              <span style="font-size: 10px"> on {{discussion.created_time | moment("LT ddd, MMM Do")}}</span>
              <v-btn
                v-if="!discussion.is_editing && discussion.user.username === $store.state.user.current.username"
                @click="edit_discussion(discussion)"
                style="justify-self: flex-end"
                icon x-small>
                <v-icon color="primary" size="15">mdi-pencil</v-icon>
              </v-btn>
              <v-btn
                v-else-if="discussion.is_editing && discussion.user.username === $store.state.user.current.username"
                @click="stop_edit_discussion(discussion)"
                style="justify-self: flex-end"
                icon x-small>
                <v-icon color="primary" size="15">mdi-close</v-icon>
              </v-btn>
            </v-card-title>
            <v-container fluid>
              <v-row>
                <v-col
                  cols="12"
                  class="pa-0 pl-1 pr-1"
                  style="min-width: 250px"
                >
                  <v-container class="pa-0" fluid>
                    <editor-menu-bar :editor="discussion_editor"
                                     v-slot="{ commands, isActive }"
                                     v-if="discussion.is_editing">
                      <div class="menubar">

                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.bold() }"
                          @click="commands.bold"
                        >
                          <v-icon size="15">mdi-format-bold</v-icon>
                        </v-btn>

                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.italic() }"
                          @click="commands.italic"
                        >
                          <v-icon size="15">mdi-format-italic</v-icon>
                        </v-btn>
                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.underline() }"
                          @click="commands.underline"
                        >
                          <v-icon size="15" name="underline" >mdi-format-underline</v-icon>
                        </v-btn>
                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.bullet_list() }"
                          @click="commands.bullet_list"
                        >
                          <v-icon size="15" name="underline" >mdi-format-list-bulleted</v-icon>
                        </v-btn>

                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.strike() }"
                          @click="commands.strike"
                        >
                          <v-icon size="18">mdi-format-strikethrough</v-icon>
                        </v-btn>
                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.code_block() }"
                          @click="commands.code_block"
                        >
                          <v-icon size="15">mdi-xml</v-icon>
                        </v-btn>
                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.paragraph() }"
                          @click="commands.paragraph"
                        >
                          <v-icon size="15">mdi-format-paragraph</v-icon>
                        </v-btn>
                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.heading({ level: 1 }) }"
                          @click="commands.heading({ level: 1 })"
                        >
                          <v-icon size="15">mdi-format-header-1</v-icon>
                        </v-btn>

                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.heading({ level: 2 }) }"
                          @click="commands.heading({ level: 2 })"
                        >
                          <v-icon size="15">mdi-format-header-2</v-icon>
                        </v-btn>

                        <v-btn
                          class="menubar__button pa-0"
                          style="width: 15px"
                          icon
                          :class="{ 'is-active': isActive.heading({ level: 3 }) }"
                          @click="commands.heading({ level: 3 })"
                        >
                          <v-icon size="15">mdi-format-header-3</v-icon>
                        </v-btn>


                      </div>
                    </editor-menu-bar>
                    <editor-content v-bind:class="{'comment-view': true, 'editing': discussion.is_editing}"
                                    class="pr-2 pl-2"
                                    :editor="discussion_editor" style="">

                    </editor-content>
                  </v-container>
                  <v-btn
                    :loading="loading_update_comment"
                    @click="update_discussion(discussion)"
                    class="mt-2 ml-2"
                    color="success"
                    x-small
                    v-if="discussion.is_editing">
                    Update
                  </v-btn>
                </v-col>
              </v-row>
            </v-container>
          </v-card>
        </v-timeline-item>
        <v-timeline-item
          v-for="comment in comment_list"
          :key="comment.id"
          color="primary"
          icon="account_circle"
        >
          <template v-slot:icon>
            <div v-if="comment && comment.user && comment.user.profile_image_thumb_url" class="mr-1">
              <v-avatar :size="39">
                <img :src="comment.user.profile_image_thumb_url"/>
              </v-avatar>
            </div>
          </template>
          <v-card>
            <v-card-title class=" d-flex align-center pa-1">
             <span style="font-size: 10px;">
                <strong>{{comment.user.first_name}}&nbsp; </strong>
              </span>
              <span style="font-size: 10px">
                on {{comment.time_created | moment("LT ddd, MMM Do")}}
              </span>

              <v-btn
                v-if="!comment.is_editing && comment.user.username === $store.state.user.current.username"
                @click="edit_comment(comment)"
                style="justify-self: flex-end"
                icon x-small>
                <v-icon size="15" color="primary">mdi-pencil</v-icon>
              </v-btn>

              <v-btn
                v-else-if="discussion.is_editing && discussion.user.username === $store.state.user.current.username"
                @click="stop_edit_comment(comment)"
                style="justify-self: flex-end"
                icon x-small>
                <v-icon color="primary" size="15">mdi-close</v-icon>
              </v-btn>
            </v-card-title>
            <v-container fluid>
              <v-row>
                <v-col
                  cols="12"
                  class="pa-0 pl-1 pr-1"
                  style="min-width: 250px"
                >
                  <v-container class="pa-0" fluid>
                    <editor-menu-bar :editor="comment.editor" v-slot="{ commands, isActive }" v-if="comment.is_editing">
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
                    <editor-content v-bind:class="{'comment-view': true, 'editing': comment.is_editing}"
                                    class="pr-2 pl-2"
                                    :editor="comment.editor"
                                    v-model="comment.content" style="">

                    </editor-content>
                  </v-container>
                  <v-btn
                    :loading="loading_update_comment"
                    @click="update_comment(comment)"
                    class="" color="success" x-small v-if="comment.is_editing">
                    Update
                  </v-btn>
                </v-col>
              </v-row>
            </v-container>
          </v-card>
        </v-timeline-item>
      </v-slide-x-transition>
    </v-timeline>
  </v-container>
</template>

<script>
  import Vue from "vue";
  import axios from "axios";
  import moment from "vue-moment";
  import {EditorContent, Editor, EditorMenuBar} from "tiptap";
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
    name: "issue_comments_list",
    model: 'discussion',
    props: {
      'project_string_id': {
        default: undefined
      },
      'discussion_id': {
        default: undefined
      },
      'discussion': {
        default: undefined
      }
    },
    components: {
      EditorContent,
      EditorMenuBar,
    },
    computed: {
      current_member: function () {

      }
    },
    watch: {
      discussion_id: {
        immediate: true,
        handler(newvalue, oldvalue) {
          if (this.$props.discussion && newvalue !== oldvalue) {
            this.discussion_editor = this.build_editor_for_discussion(this.$props.discussion)
          }
          this.fetch_comments(newvalue);

        }
      },
    },
    methods: {
      build_editor_for_discussion: function (discussion) {
        return new Editor({
          editable: false,
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
          content: discussion.description,
        })
      },
      build_editor_for_comment: function (comment) {
        return new Editor({
          editable: false,
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
          content: comment.content,
        })
      },
      edit_comment(comment) {
        comment.editor.setOptions({
          editable: true
        })
        this.$store.commit('set_user_is_typing_or_menu_open', true);
        Vue.set(comment, 'is_editing', true);
      },
      edit_discussion(discussion) {
        this.discussion_editor.setOptions({
          editable: true
        })
        this.$store.commit('set_user_is_typing_or_menu_open', true);
        Vue.set(discussion, 'is_editing', true);
      },
      stop_edit_discussion(discussion) {
        this.discussion_editor.setOptions({
          editable: true
        })
        this.$store.commit('set_user_is_typing_or_menu_open', false);
        Vue.set(discussion, 'is_editing', false);
      },
      stop_edit_comment(comment) {
        comment.editor.setOptions({
          editable: false
        })
        this.$store.commit('set_user_is_typing_or_menu_open', false);
        Vue.set(comment, 'is_editing', false);
      },
      async update_discussion(discussion){
        this.loading_update_comment = true;
        this.list_comments_error = {}
        // if we don't reset list_comments_error then if success old error shows I think
        try {
          const result = await axios.post(`/api/v1/project/${this.$props.project_string_id}/discussion/${this.$props.discussion_id}/update`, {
            description: this.discussion_editor.getHTML(),
            attached_elements: this.$props.discussion.attached_elements
          })
          if (result.status === 200) {
            const discussion_updated = result.data.discussion;
            this.$emit('comment_updated', discussion_updated);
            this.$store.commit('set_user_is_typing_or_menu_open', false);
            Vue.set(discussion, 'is_editing', false);
          }

        } catch (error) {
          this.list_comments_error = this.$route_api_errors(error)
          console.log(error)

        } finally {
          this.loading_update_comment = false;

        }
      },
      async update_comment(comment) {
        this.loading_update_comment = true;
        this.list_comments_error = {}
        try {
          const result = await axios.post(`/api/v1/project/${this.$props.project_string_id}/discussion/${this.$props.discussion_id}/update-comment`, {
            content: comment.editor.getHTML(),
            comment_id: comment.id
          })
          if (result.status === 200) {
            const comment_updated = result.data.comment;
            this.$emit('comment_updated', comment_updated);
            this.$store.commit('set_user_is_typing_or_menu_open', false);
            Vue.set(comment, 'is_editing', false);
          }

        } catch (error) {
          this.list_comments_error = this.$route_api_errors(error)
          console.log(error)

        } finally {
          this.loading_update_comment = false;

        }

      },
      add_comment(comment) {
        this.comment_list.push({
          ...comment,
          editor: this.build_editor_for_comment(comment)
        })
      },
      async fetch_comments(discussion_id) {
        if(!discussion_id){
          return
        }
        if(this.comment_list.length > 0){
          this.comment_list.forEach(comment =>{
            try{
              if(comment.editor){
                comment.editor.destroy()
              }
            }catch (e) {}
          })
        }
        this.comment_list = [];
        this.loading_comments = true;
        try {
          const project_string_id = this.$props.project_string_id;
          const result = await axios.post(`/api/v1/project/${project_string_id}/discussion/${discussion_id}/comments`, {})
          if (result.status === 200) {
            this.comment_list = result.data.comments;
            this.comment_list = this.comment_list.map(comment => {
              return {
                ...comment,
                editor: this.build_editor_for_comment(comment)
              }
            })
          }

        } catch (error) {
          this.list_comments_error = this.$route_api_errors(error)
          console.log(error);
        } finally {
          this.loading_comments = false;
        }
      }
    },
    data() {
      return {
        comment_list: [],
        loading_comments: false,
        discussion_editor: undefined,
        loading_update_comment: false,
        list_comments_error: {},
      }
    },
    beforeDestroy() {
      if(this.comment_list){
        this.comment_list = this.comment_list.map(comment => {
          try{
            if(comment.editor){
              comment.editor.destroy()
            }
          }catch (e) {}
          return comment
        })
      }
    },
    mounted() {

    },
  })
</script>

<style>
  .comment-view .ProseMirror {
    border: none;
    outline: none;
    min-height: 100%;
    width: 80%;
    background-color: #fafbfc;
  }

  .comment-view .ProseMirror p {
    margin: 0 !important;
  }

  .comment-view .ProseMirror.focus-visible.ProseMirror-focused {
    white-space: pre-wrap;
    min-height: 100%;
    width: 100%;
    background-color: #fafbfc;
  }

  .comment-view.editing .ProseMirror.focus-visible.ProseMirror-focused {
    white-space: pre-wrap;
    min-height: 150px;
    padding: 1rem;
    width: 80%;
    background-color: #fafbfc;
    border: 1px solid #0366d6;
    border-radius: 15px;
    box-shadow: #bad1f3;
  }
</style>
