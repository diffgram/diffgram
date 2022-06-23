import { get_action_template } from '../../../services/workflowServices'

const action_mixin = {
  props: {
    prev_action: {
      default: null
    },
    action: {
      required: true
    },
    project_string_id: {
      required: true
    },
    actions_list: {
      required: true
    },
    display_mode: {
      default: "wizard"
    }
  },
  data: () => ({
    loading: false,
    action_template: null
  }),
  methods: {
    on_action_updated: function (act) {
      this.$emit('action_updated', act)
    },
    get_action_template: async function (){
      if(!this.action){
        throw new Error("Cannot get action_template. Action is undefined.")
      }
      let [res, err] = await get_action_template(this.project_string_id, this.action.template_id)
      if (err){
        console.error(err)
        return
      }
      this.action_template = res.action_template
    }
  },
  computed: {}
}
export default action_mixin;
