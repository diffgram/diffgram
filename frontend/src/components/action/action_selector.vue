<template>

  <div class="pr-6 pl-6" style="min-height: 850px">
    <v_error_multiple :error="error"></v_error_multiple>
    <v-text-field label="Search for an action..." v-model="search"></v-text-field>

    <v-container fluid class="d-flex flex-wrap" v-if="!loading">
      <action_step_box v-for="action in actions_list_filtered"
                       @add_action_to_workflow="add_action_to_workflow(action)"
                       style="width: 250px; height: 250px"
                       :action="action"
      >

      </action_step_box>
    </v-container>
    <v-container v-else>
      <v-progress-linear indeterminate></v-progress-linear>
    </v-container>
  </div>

</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
import action_step_box from "./action_step_box.vue";
import {Action} from "./Action";
import {action_template_list} from './../../services/workflowServices';
export default Vue.extend({

    name: 'action_config_dialog',
    components: {
      action_step_box

    },
    props: ['action', 'project_string_id'],

    async mounted() {
      await this.api_action_template_list()
    },

    data() {
      return {
        is_open: false,
        loading: false,
        search: '',
        error: null,
        actions_template_list: [],
        actions_list: [
          new Action(
            'Human Labeling Task',
            'mdi-brush',
            'create_task',
            {
              trigger_event_name: 'file_uploaded',
              upload_directory_id_list: null,
              trigger_action_id: null,
            },
            {event_name: null},
              'Human Tasks',
            {event_name: 'task_completed'}
          ),
          new Action(
            'JSON Export',
            'mdi-database-export-outline',
            'export',
            {
              trigger_event_name: 'task_completed',
              upload_directory_id_list: null,
              trigger_action_id: null,
            },
            {event_name: 'all_tasks_completed'},
            'Create JSON export from labeled data.',
            {event_name: 'export_generate_success'}
          )
        ],
      }
    },
    watch: {

    },
    computed: {
      actions_list_filtered: function(){
        if(!this.search || this.search === ''){
          return this.actions_template_list
        }
        return this.actions_template_list.filter(elm => elm.title.toLowerCase().includes(this.search.toLowerCase()))
      }
    },
    methods: {
      build_actions_list: function(action_template_list){
        this.actions_template_list = [];
        for(let template of action_template_list){
          let action = new Action(
            template.public_name,
            template.icon,
            template.kind,
            template.trigger_data,
            template.condition_data,
            template.description,
            template.completion_condition_data
          )
          action.id = template.id
          this.actions_template_list.push(action)
        }
      },
      api_action_template_list: async function(){

        let [result, err] = await action_template_list(this.project_string_id)
        if(err){
          this.error = this.$route_api_errors(err);
          return
        }
        if(result){
          result.action_template_list.push(
            {
              description: "Automatically extract printed text, handwriting, and data from any document",
              kind: "temp_action",
              public_name: "AWS Texttract",

              icon: "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png"

            },
            {
              description: "Add prelabeled data to text files using Azure Text Analytics",
              kind: "temp_action",
              public_name: "Prelabel with Azure Text Analytics",
              icon: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Microsoft_Azure.svg/1200px-Microsoft_Azure.svg.png"
            },
            {
              description: "Add Labels with Vertex AI (Google)",
              kind: "temp_action",
              public_name: "Vertex AI Prediction",
              icon: "https://techcrunch.com/wp-content/uploads/2021/05/VertexAI-512-color.png"
            },
            {
              public_name: "HuggingFace ZeroShot Classification",
              kind: "temp_action",
              description: "SST2 sentiment (distilbert-base-uncased-finetuned-sst-2-english)",
              icon: "https://huggingface.co/front/assets/huggingface_logo-noborder.svg"
            },
            {
              public_name: "HuggingFace Tokens",
              kind: "temp_action",
              description: "dbmdz/bert-large-cased-finetuned-conll03-english",
              icon: "https://huggingface.co/front/assets/huggingface_logo-noborder.svg"
            },
            {
              public_name: "HuggingFace Transformers (Custom)",
              kind: "temp_action",
              description: "Choose own Transformer",
              icon: "https://huggingface.co/front/assets/huggingface_logo-noborder.svg"
            },
            {
              public_name: "Cleanlab",
              kind: "temp_action",
              description: "cleanlab automatically finds and fixes errors in any ML dataset.",
              icon: "https://cleanlab.ai/favicon.ico"
            },
            {
              public_name: "Weakly Supervise NER",
              kind: "temp_action",
              description: " Instead of annotating texts by hand, we define a set of labelling functions to automatically label our documents.",
              icon: "https://raw.githubusercontent.com/NorskRegnesentral/skweak/main/data/skweak_logo.jpg"
            },
            {
              public_name: "Publish Event",
              kind: "temp_action",
              description: "Publish event to Kafka or AMQP to integrate with other services.",
              icon: "data:image/png;base64,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"
            },
            {
              public_name: "HTTP Request",
              kind: "temp_action",
              description: "Send an HTTP request to an external service (Webhook).",
              icon: "https://www.integromat.com/en/academy/wp-content/uploads/2020/08/Screen_Shot_2020-08-03_at_10.38.48_AM-426x394.png"
            },
            {
              public_name: "Sample Data Subset",
              kind: "temp_action",
              description: "Sample a portion of the data based on a query or rule.",
              icon: "https://res.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_170,w_170,f_auto,b_white,q_auto:eco,dpr_1/okhxici7vjqqznihxezz"
            },
            {
              public_name: "Manual Approval Control",
              kind: "temp_action",
              description: "Require multiple approvals before workflow continues or restarts.",
              icon: "https://res.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_170,w_170,f_auto,b_white,q_auto:eco,dpr_1/okhxici7vjqqznihxezz"
            },
            {
              public_name: "Custom Integration",
              kind: "temp_action",
              description: "Read the docs on how to add your own custom actions.",
              icon: "https://res.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_170,w_170,f_auto,b_white,q_auto:eco,dpr_1/okhxici7vjqqznihxezz"
            },
            {
              public_name: "Train Vertex AI AutoML",
              kind: "temp_action",
              description: "Train Vertex AI AutoML",
              icon: "https://techcrunch.com/wp-content/uploads/2021/05/VertexAI-512-color.png"
            },
            {
              public_name: "Train A Custom Model",
              kind: "temp_action",
              description: "Train A Custom Model",
              icon: "https://res.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_170,w_170,f_auto,b_white,q_auto:eco,dpr_1/okhxici7vjqqznihxezz"
            },
            {
              public_name: "Analysis & Reports",
              kind: "temp_action",
              description: "Schedule, modify, view report data",
              icon: "https://res.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_170,w_170,f_auto,b_white,q_auto:eco,dpr_1/okhxici7vjqqznihxezz"
            },
            {
              public_name: "Share Data View",
              kind: "temp_action",
              description: "Shareable custom data views based on defined rules.",
              icon: "https://res.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_170,w_170,f_auto,b_white,q_auto:eco,dpr_1/okhxici7vjqqznihxezz"
            },
          )
          this.build_actions_list(result.action_template_list)
        }

      },
      add_action_to_workflow: function(act){
        if (act.kind == "temp_action") { return }
        this.$emit('add_action_to_workflow', act)
        this.close();
      },
      close() {
        this.input = undefined;
        this.is_open = false;
      },
      open() {
        this.is_open = true;
      },
    }
  }
) </script>


<style>
code{
  width: 100%;
  height: 100% !important;
}
</style>
