import dataset_selector from "../../components/concrete/dataset/dataset_selector.vue";

export default {
  title: "Concrete/dataset_selector",
  component: dataset_selector,
};

export const Default = (args, { argTypes }) => ({
  components: {
    dataset_selector,
  },
  props: Object.keys(argTypes),
  template: '<dataset_selector v-bind="$props" />',
});