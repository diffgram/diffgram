<template>
  <v-container class="d-flex" fluid>
    <div v-if="$store.state.user.current.profile_image_thumb_url">
      <v-avatar size="36">
        <img :src="$store.state.user.current.profile_image_thumb_url" />
      </v-avatar>
    </div>
    <div v-else>
      <v-icon  large>account_circle</v-icon>
    </div>

    <v-container style="width: 100%" class="d-flex flex-column pa-0" fluid>
      <v-container  class="d-flex justify-end pb-0 pr-4" fluid>

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
      <editor-content :editor="editor" v-model="content" class="comment-create">

      </editor-content>
      <v_error_multiple :error="create_comment_error">
      </v_error_multiple>
      <div class="d-flex align-center justify-end">
        <v-btn width="30%"
               class="mt-2 mr-4 align-self-end"
               small
               v-if="discussion && discussion.status !== 'closed'"
               color="error"
               :disabled="editor.getHTML() === ''"
               :loading="loading_update_discusssion"
               @click="close_discussion">
          Close
        </v-btn>
        <v-btn width="30%"
               class="mt-2 align-self-end"
               small
               color="success"
               :disabled="editor.getHTML() === ''"
               :loading="loading_create_comment"
               @click="create_comment">
          Comment
        </v-btn>
      </div>


    </v-container>
  </v-container>
</template>

<script>
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
    History,
  } from 'tiptap-extensions'
  import Vue from "vue";
  import axios from 'axios';

  export default Vue.extend( {
    name: "discussion_comments",
    props:{
      'project_string_id':{
        default: undefined
      },
      'discussion_id': {
        type: Number
      },
      'discussion': {
        type: Object,
        default: undefined
      },
    },
    computed:{
      current_member: function(){

      }
    },
    components: {
      EditorContent,
      EditorMenuBar,
      EditorMenuBubble,
    },
    methods: {
      focus_comment_box: function(){
        this.$store.commit('set_user_is_typing_or_menu_open', true);
      },
      focus_out_comment_box: function(){
        this.$store.commit('set_user_is_typing_or_menu_open', false);
      },
      close_discussion: async function(){
        this.loading_update_discusssion = true;
        try {
          const result = await axios.post(`/api/v1/project/${this.$props.project_string_id}/discussion/${this.$props.discussion_id}/update`, {
            description: undefined,
            attached_elements: undefined,
            status: 'closed'
          })
          if (result.status === 200) {
            const discussion_updated = result.data.discussion;
            this.$emit('discussion_updated', discussion_updated);
            this.$store.commit('set_user_is_typing_or_menu_open', false);
          }

        } catch (error) {
          this.create_comment_error = this.$route_api_errors(error)
          console.log(error)

        } finally {
          this.loading_update_discusssion = false;

        }
      },
      create_comment: async function(){
        this.loading_create_comment = true;
        try{
          const result = await axios.post(`/api/v1/project/${this.$props.project_string_id}/discussion/${this.$props.discussion_id}/add-comment`,{
            content: this.editor.getHTML(),
          })
          if(result.status === 200){
            const comment = result.data.comment;
            this.$emit('comment_created', comment);
            this.editor.setContent('');
          }

        }
        catch (error) {
          this.create_comment_error = this.$route_api_errors(error)
          console.log(error)

        }
        finally {
          this.loading_create_comment = false;
        }

      },

    },
    data() {
      return {
        loading_create_comment: false,
        loading_update_discusssion: false,
        content: '',
        create_comment_error: {},
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
          onFocus: this.focus_comment_box,
          onBlur: this.focus_out_comment_box,
        }),

      }
    },
    beforeDestroy() {
      if(this.editor){
        try{
          this.editor.destroy()
        }catch (e) {

        }
      }

    },
    mounted() {

    },
  })
</script>

<style>
  .comment-create .ProseMirror{
    border: none;
    outline: none;
    min-height: 100%;
    width: 100%;
    background-color: #ebebeb;
    border: 1px solid #0366d6;
    border-radius: 15px;
    padding: 1rem;
  }
  .comment-create .ProseMirror p{
    margin: 0 !important;
  }
  .comment-create .ProseMirror.focus-visible.ProseMirror-focused{
    white-space: pre-wrap;
    min-height: 100%;
    width: 100%;
    background-color: #ebebeb;
    border: 1px solid #0366d6;
    border-radius: 15px;
    box-shadow: #bad1f3;
  }
  .menubar{
    margin-bottom: 5px;
  }

</style>
