<template>
  <!-- Import Connection Configuration -->
  <div class="mb-4">
    <h2 class="font-weight-light mb-4">3. Import Connection Configuration: </h2>
    <!-- Wrapper for connection configuration inputs -->
    <div class="d-flex flex-column ml-10 pl-8 pa-4" style="border: 1px solid #e0e0e0; width: 80%">
      <!-- Global dataset selector component -->
      <global_dataset_selector
        v-model="action.config_data.directory_id"
        @change_directory="on_change_directory"
      />
      <!-- Connection selector component -->
      <connection_select :project_string_id="project_string_id" v-model="action.config_data.connection"/>

      <!-- Diffgram database name selector component -->
      <diffgram_select
        v-if="action.config_data.connection && action.config_data.connection.id"
        :item_list="db_names_list"
        :return_object="false"
        value="name"
        name_key="name"
        v-model="action.config_data.db_name"
        label="Database Name"
        :disabled="loading"
      >
      </diffgram_select>

      <!-- Diffgram collection name selector component -->
      <diffgram_select
        v-if="action.config_data.connection && action.config_data.connection.id && action.config_data.db_name"
        :item_list="collections_names_list"
        :return_object="false"
        value="name"
        name_key="name"
        v-model="action.config_data.collection_name"
        label="Collection Name"
        :disabled="loading"
      >
      </diffgram_select>

      <!-- Conditional rendering of the mapping table -->
      <div v-if="action.config_data.connection && action.config_data.connection.id &&
                    action.config_data.db_name &&
                    action.config_data.collection_name">
        <h4>Map You Collection Keys: </h4>
        <!-- Data table for mapping Diffgram file fields to MongoDB collection fields -->
        <v-data-table
          :hide-default-footer="true"
          :headers="headers"
          :items="items" hide-actions>
          <template v-slot:item="props">
            <tr>
              <td>{{ props.item.label }}</td>
              <td class="ma-auto">
                <!-- Text field for inputting the MongoDB collection field value -->
                <v-text-field v-model="action.config_data.key_mappings[props.item.value]" outlined single-line ></v-text-field>
              </td>
            </tr>
          </template>
        </v-data-table>
      </div>

    </div>
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
        // Headers for the data table
        {text: 'Diffgram File Field', value: 'diffgram_field'},
        {text: 'Mongo DB Collection Field', value: 'value'},
      ],
      items: [
        // Predefined items for the data table
        {label: 'File name', value: 'file_name'},
        {label: 'Text Data', value: 'text_data'},
        {label: 'Reference ID', value: 'reference_id'},
      ],
    }
  },
  methods: {
    on_change_directory: function(dir){
      // Callback function for global dataset selector component
      this.action.config_data.directory_id = dir.directory_id
    },
    get_mongo_databases: async function (connection) {
      // Fetch the list of databases for the given MongoDB connection
      if (!connection) {
        return
      }
      const [db_list_data, err] = await get_mongo_database_list(connection.id)
      this.db_names_list = db_list_data.data.map(name => ({name: name, value: name}))
    },
    get_mongo_collections: async function (connection, db_name) {
      // Fetch the list of collections for the given MongoDB connection and database
      if (!connection) {
        return
      }
      const [collection_list_data, err] = await get_mongo_collections_list(connection.id, db_name)
      this.collections_names_list = collection_list_data.data.map(name => ({name: name, value: name}))
    }
  }
  ,
  async mounted() {
    // Initialize the steps configuration and set up key mappings if not already set
    this.steps_config = new ActionStepsConfig()
    if (!this.action.config_data.key_mappings) {
      this.action.config_data.key_mappings = {}
    }
    if(this.action.config_data.connection){
      // Fetch the list of databases when the component is mounted if a connection is already set
      await this.get_mongo_databases(this.action.config_data.connection)
    }

    if(this.action.config_data.db_name){
      // Fetch the list of collections when the component is mounted if a database name is already set
      await this.get_mongo_collections(this.action.config_data.connection, this.action.config_data.db_name)
    }
  }
}
</script>
