import dataset_selector from "../../components/concrete/dataset/dataset_selector.vue";

export default {
  title: "Concrete/dataset_selector",
  component: dataset_selector
};

export const Default = (args, { argTypes }) => ({
  components: {
    dataset_selector,
  },
  props: Object.keys(argTypes),
  template: '<dataset_selector v-bind="$props" />',
});
Default.args = {
  dataset_list: [
    { directory_id: '1', nickname: 'Dataset 1', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '2', nickname: 'Dataset 2', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '3', nickname: 'Dataset 3', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '4', nickname: 'Dataset 4', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '5', nickname: 'Dataset 5', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '6', nickname: 'Dataset 6', created_time:"2022-10-10T19:12:44.257372" },
  ],
};