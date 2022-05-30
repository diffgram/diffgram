<template>
  <div>
    <v-card :class="`pa-2 node-card` "
            @click="select_action(action)"
            style="position: relative; width: 250px"
            >
      <v-btn class="config-btn" color="primary"  icon  x-small @click="open_config_dialog"><v-icon color="primary">mdi-cog</v-icon></v-btn>

      <v-card-title class="d-flex justify-start">
        <v-img style="width: 10%"  :src="action.icon"></v-img>
        <h4 class="ml-4" style="width: 80%">
          {{action.public_name}}
        </h4>
      </v-card-title>


      <button_with_confirm
        v-if="action.kind !== 'action_start'"
        tooltip_message="Archive Workflow"
        button_message="Archive Workflow"
        @confirm_click="remove"
        icon="mdi-delete"
        button_color="error"
        :icon_style="true"
        datacy_confirm="archive_schema_button_confirm"
        datacy="archive_schema_button"
      >
      </button_with_confirm>
      <div v-if="is_last_node" class=" last-step-arrow d-flex flex-column justify-center align-center">
        <v-icon size="46">mdi-arrow-down</v-icon>
        <v-btn @click="open_action_selector" x-large icon color="secondary" ><v-icon>mdi-plus</v-icon></v-btn>
      </div>
    </v-card>

      <action_config_dialog
        ref="action_config_dialog"
        :action="action"
        :actions_list="actions_list"
        :project_string_id="project_string_id">

      </action_config_dialog>
  </div>

</template>

<script>

import action_config_dialog from "@/components/action/actions_config_base/action_config_dialog";
export default {
  name: "action_node_box",
  components: {
    action_config_dialog

  },
  props: ['node', 'action', 'actions_list', 'project_string_id'],
  mounted() {

  },
  methods: {
    select_action: function(act){
      this.$emit('select_action', act)
    },
    add_action_to_workflow: function(act){
     this.$emit('add_action_to_workflow', act)
    },
    open_action_selector: function(e){
      e.stopPropagation()
      this.$emit('open_action_selector')
    },
    remove: function(e){
      e.stopPropagation()
      this.$emit('remove', this.action)
    },
    open_config_dialog: function(e){
      e.stopPropagation()
      this.$refs.action_config_dialog.open()
    }

  },
  computed: {
    is_last_node: function(){
      return this.actions_list.indexOf(this.action) === this.actions_list.length - 1
    }
  }
}
</script>

<style scoped>
.last-step-arrow {
  position: absolute;
  bottom: -100px;
  left: 40%;
}
.node-card:hover{
  background: #a1cdff;
  cursor: pointer;
  transition: 0.5s ease;
  position: relative;
}
.action-start{
  background: #efebe9 !important;
}
.config-btn{
  position: absolute;
  top: 0;
  right: 0;
  padding: 1rem;
}
</style>
