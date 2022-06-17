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
  }),
  methods: {
    on_action_updated: function (act) {
      this.$emit('action_updated', act)
    },
  },
  computed: {}
}
export default action_mixin;
