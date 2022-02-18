<template>

  <v-dialog v-model="show_share_instance_menu"
            max-width="450px"
            @click:outside="$emit('click:outside', $event)"
            >
    <v-card>
      <v-card-title class="headline">Share Instance</v-card-title>
      <v-card-text>
        <v-select
          data-cy="share_mode_select"
          :items="share_types"
          v-model="share_type"
          item-text="name"
          item-value="value"
          label="Sharing Mode"
        >
        </v-select>
        Use the following to share your instance:
        <v-container v-if="share_type === 'copy'">
          <div class="link" style="position: relative">
            <v-btn @click="copy_text()" small color="primary" style="position: absolute; top: 0; right: 0;">
              <v-icon size="15">mdi-content-copy</v-icon>
            </v-btn>
            <kbd
              class="d-flex align-center justify-start text-left"
              style="font-size: 10px; height: 50px">{{share_instance_url}}</kbd>
          </div>
          <p v-if="show_copy_success" class="font-weight-bold text--success">Copied!</p>
        </v-container>
        <v-container v-if="share_type === 'email'">
          <member_select
            data-cy="member_select"
            v-model="member_list_ids"
            :member_list="$store.state.project.current.member_list"
            :multiple="true"
            :init_all_selected="true"
            :allow_all_option="true"
          ></member_select>
          <v-textarea data-cy="share_instance_textarea" v-model="notes" background-color="#fefefe" label="Add a message..."></v-textarea>
        </v-container>

      </v-card-text>

      <v_error_multiple :error="error">
      </v_error_multiple>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="green darken-1"
          text
          data-cy="start-importing"
          @click="close_share_dialog()"
        >
          Close
        </v-btn>
        <v-btn
          v-if="share_type === 'email'"
          color="green darken-1"
          text
          :loading="loading_send_email"
          data-cy="share_instance_button"
          @click="email_link"
        >
          Email Members
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import Vue from "vue";
  import axios from '../../services/customAxiosInstance';

  export default Vue.extend({
      name: 'members_list',
      props: {
        'show_share_instance_menu': {
          default: null
        },
        'project_string_id': {
          default: undefined
        }
      },
      data: function () {
        return {
          share_types: [
            {name: 'Email Project Members', value: 'email'},
            {name: 'Copy Link', value: 'copy'},
          ],
          share_type: 'email',
          notes: '',
          share_instance_url: '',
          member_list_ids: [],
          loading_send_email: false,
          show_copy_success: false,
          error: {}
        }
      },
      mounted() {
        this.share_instance_url = `https://diffgram.com${this.$route.fullPath}`;
        this.show_copy_success = false;

      },
      computed: {
        project_string_id_from_task(){
          if(this.$props.project_string_id){
            return this.$props.project_string_id
          }
          return this.$store.state.project.current.project_string_id;
        },
        current_mode () {
          return this.$store.getters.get_current_mode;
        },
      },
      methods: {
        copyToClipboard: function (value) {
          // https://stackoverflow.com/questions/47879184/document-execcommandcopy-not-working-on-chrome/47880284
          const el = document.createElement('textarea');
          el.value = value;
          el.textContent = value;
          document.body.appendChild(el);

          var selection = document.getSelection();
          var range = document.createRange();
          range.selectNode(el);
          selection.removeAllRanges();
          selection.addRange(range);

          document.execCommand('copy')
          selection.removeAllRanges();

          document.body.removeChild(el);
        },
        copy_text: function () {
          this.copyToClipboard(this.share_instance_url);
          this.show_copy_success = true;
        },
        close_share_dialog: function () {
          this.$emit('share_dialog_close')
        },
        async email_link() {
          this.loading_send_email = true;
          this.error = {}

          const project_string_id = this.project_string_id_from_task;
          try {
            let url = '';
            if (this.current_mode === 'trainer' && this.$props.task) {
              url = `/api/task/${this.$props.task.id}/share-link`;
            } else if (this.current_mode === 'builder') {
              url = `/api/project/${project_string_id}/share-link`;
            } else {
              return;
            }
            const response = await axios.post(url, {
              member_list: this.member_list_ids,
              message: this.notes,
              link: this.share_instance_url,
            })
            if (response.data) {
              this.close_share_dialog();
              this.notes = '';
            }
          } catch (error) {
            this.error = this.$route_api_errors(error)
          } finally {
            this.loading_send_email = false;
          }

        },
      }
    }
  )
</script>

<style scoped>

</style>
