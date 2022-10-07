import standard_button from "../components/base/standard_button.vue";

export default {
  title: "Base/StandardButton",
  component: standard_button,
};

export const StandardButton = (args, { argTypes }) => ({
  components: {
    standard_button,
  },
  props: Object.keys(argTypes),
  template: '<standard_button v-bind="$props" />',
});
