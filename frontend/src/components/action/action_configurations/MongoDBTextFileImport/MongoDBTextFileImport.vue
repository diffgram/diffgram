<template>
  <div class="d-flex flex-column" style="height: 100%">

    <action_config_base
      v-if="steps_config"
      :project_string_id="project_string_id"
      :display_mode="display_mode"
      @open_action_selector="$emit('open_action_selector')"
      :steps_config="steps_config.generate()"
      :actions_list="actions_list"
      :action="action">

      <template v-slot:wizard_action_config>
        <mongo_db_text_import_config_details
          :actions_list="actions_list"
          :action="action"
          :project_string_id="project_string_id"></mongo_db_text_import_config_details>
      </template>

      <template v-slot:ongoing_usage>

      </template>

    </action_config_base>
  </div>
</template>

<script>
import action_config_base from "@/components/action/actions_config_base/action_config_base";
import action_config_mixin from "../action_config_mixin";
import mongo_db_text_import_config_details from "./mongo_db_text_import_config_details.vue";
import ActionStepsConfig from '../ActionStepsConfig';

export default {
  name: "MongoDBTextFileImport",
  mixins: [action_config_mixin],
  components: {
    action_config_base,
    mongo_db_text_import_config_details,
  },
  props: {
    action:{
      required: true,
    },
    project_string_id: {
      required: true
    },
  },
  data (){
    return {
      steps_config: null,
    }
  },
  mounted() {
    this.steps_config = new ActionStepsConfig()
  }
}
</script>
