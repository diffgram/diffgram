import label_schema_selector from "../../components/label/label_schema_selector";

const project_string_id = 'storybook-mock'

let schema_list = [
  { 
    id: 1, 
    name: 'Default', 
    is_default: true,
  },
  { 
    id: 2, 
    name: 'Trial schema',
  }
]

export default {
  title: "Concrete/label_schema_selector",
  component: label_schema_selector,
  parameters: {
    mockData: [
      {
        url: `/api/v1/project/${project_string_id}/labels-schema`,
        method: 'GET',
        status: 200,
        response: schema_list
      }
    ]
  }
};

export const Default = (args, { argTypes }) => ({
  components: {
    label_schema_selector,
  },
  props: Object.keys(argTypes),
  template: '<label_schema_selector v-bind="$props" />',
});
Default.args = {
  project_string_id,
};
