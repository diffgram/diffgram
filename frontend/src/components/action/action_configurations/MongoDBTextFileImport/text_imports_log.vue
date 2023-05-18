<template>
  <div class="mb-4">
   <v_input_view :project_string_id="project_string_id" :workflow_id="action.workflow_id" :action_id="action.id">

   </v_input_view>
  </div>
</template>

<script>
import action_config_base from "@/components/action/actions_config_base/action_config_base";
import action_config_mixin from "../action_config_mixin";
import ActionStepsConfig from '../ActionStepsConfig';
import global_dataset_selector from "@/components/attached/global_dataset_selector.vue";
import {get_mongo_database_list, get_mongo_collections_list} from "@/services/mongoDBConnectionServices";

export default {
  name: "mongo_db_text_import_config_details",
  mixins: [action_config_mixin],
  components: {
    global_dataset_selector,
    action_config_base,
  },
  props: {
    action: {
      required: true,
    },
    project_string_id: {
      required: true
    },
  },
  watch: {
    'action.config_data.connection': {
      handler: function (newVal, oldVal) {
        this.get_mongo_databases(newVal)
      },
      deep: true
    },
    'action.config_data.db_name': {
      handler: function (newVal, oldVal) {
        this.get_mongo_collections(this.action.config_data.connection, newVal)
      },
      deep: true
    },
  },
  data() {
    return {
      db_names_list: [],
      collections_names_list: [],
      headers: [
        {text: 'Diffgram File Field', value: 'diffgram_field'},
        {text: 'Mongo DB Collection Field', value: 'value'},
      ],
      items: [
        {label: 'File name', value: 'file_name'},
        {label: 'Text Data', value: 'text_data'},
        {label: 'Reference ID', value: 'reference_id'},
      ],
    }
  },
  methods: {
    on_change_directory: function(dir){
      this.action.config_data.directory_id = dir.directory_id
    },
    get_mongo_databases: async function (connection) {
      if (!connection) {
        return
      }
      const [db_list_data, err] = await get_mongo_database_list(connection.id)
      this.db_names_list = db_list_data.data.map(name => ({name: name, value: name}))
    },
    get_mongo_collections: async function (connection, db_name) {
      if (!connection) {
        return
      }
      const [collection_list_data, err] = await get_mongo_collections_list(connection.id, db_name)
      this.collections_names_list = collection_list_data.data.map(name => ({name: name, value: name}))
    }
  }
  ,
  async mounted() {
    this.steps_config = new ActionStepsConfig()
    if (!this.action.config_data.key_mappings) {
      this.action.config_data.key_mappings = {}
    }
    if(this.action.config_data.connection){
      await this.get_mongo_databases(this.action.config_data.connection)
    }

    if(this.action.config_data.db_name){
      await this.get_mongo_collections(this.action.config_data.connection, this.action.config_data.db_name)
    }
  }
}
</script>
