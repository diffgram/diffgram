<template>
  <div class="mb-4">
    <h2 class="font-weight-light mb-4">3. Import Connection Configuration: </h2>
    <div class="d-flex flex-column ml-10 pl-8 pa-4" style="border: 1px solid #e0e0e0; width: 80%">
      <connection_select :project_string_id="project_string_id" v-model="action.config_data.connection"/>
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
      <div v-if="action.config_data.connection && action.config_data.connection.id &&
                    action.config_data.db_name &&
                    action.config_data.collection_name">
        <h4>Map You Collection Keys: </h4>
        <v-data-table
          :hide-default-footer="true"
          :headers="headers"
          :items="items" hide-actions>
          <template v-slot:item="props">
            <tr>
              <td>{{ props.item.label }}</td>
              <td class="ma-auto">
                <v-text-field v-model="props.item.value" outlined single-line ></v-text-field>
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
        {text: 'Diffgram File Field', value: 'diffgram_field'},
        {text: 'Mongo DB Collection Field', value: 'value'},
      ],
      items: [
        {label: 'File name', value: ''},
        {label: 'Text Data', value: ''},
        {label: 'Reference ID', value: ''},
      ],
    }
  },
  methods: {
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
    if (!this.action.config_data.key_mapping) {
      this.action.config_data.key_mapping = {}
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
