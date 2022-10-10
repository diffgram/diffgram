import standard_chip from "../../components/base/standard_chip.vue";

export default {
  title: "Attached/dataset_selector",
  component: standard_chip,
};

export const Default = (args, { argTypes }) => ({
  components: {
    standard_chip,
  },
  props: Object.keys(argTypes),
  template: '<standard_chip v-bind="$props" />',
});

Default.args = {
    message: "Diffgram standard chip"
}