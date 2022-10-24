import label_select_annotation from "../../components/label/label_select_annotation";

const project_string_id = 'storybook-mock'

const label_list = [
  { 
    id: 1, 
    label: {
        id: 2,
        name: "First"
    },
    colour: {
        hex: "#00FF80"
    }
  },
]

export default {
  title: "Concrete/label_select_annotation",
  component: label_select_annotation,
  parameters: {
    mockData: [
      {
        url: `/api/project/${project_string_id}/labels`,
        method: 'GET',
        status: 200,
        response: {
            labels_out: label_list
        }
      }
    ]
  }
};

export const Default = (args, { argTypes }) => ({
  components: {
    label_select_annotation,
  },
  props: Object.keys(argTypes),
  template: '<label_select_annotation v-bind="$props" />',
});
Default.args = {
  project_string_id,
};
