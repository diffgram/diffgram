import standard_chip from "../components/base/standard_chip.vue";

export default {
  title: "Base/StandardChip",
  component: standard_chip,
};

export const StandardChip = (args, { argTypes }) => ({
  components: {
    standard_chip,
  },
  props: Object.keys(argTypes),
  template: '<standard_chip v-bind="$props" />',
});

StandardChip.args = {
    message: "Diffgram standard chip"
}