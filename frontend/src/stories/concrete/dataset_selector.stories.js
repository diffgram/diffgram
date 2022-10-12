import dataset_selector from "../../components/concrete/dataset/dataset_selector.vue";

const project_string_id = 'storybook-mock'

export default {
  title: "Concrete/dataset_selector",
  component: dataset_selector,
  parameters: {
    mockData: [
      {
        url: `/api/v1/project/${project_string_id}/directory/new`,
        method: 'POST',
        status: 200,
        response: (request) => {
          const request_body = JSON.parse(request.body)
          return {
              log: {
                success: true,
              },
              new_directory: {
                nickname: request_body.nickname
              }
          }
        }
      }
    ]
  }
};

export const Default = (args, { argTypes }) => ({
  components: {
    dataset_selector,
  },
  props: Object.keys(argTypes),
  template: '<dataset_selector v-bind="$props" />',
});
Default.args = {
  project_string_id,
  show_new: true,
  dataset_list: [
    { directory_id: '1', nickname: 'Dataset 1', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '2', nickname: 'Dataset 2', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '3', nickname: 'Dataset 3', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '4', nickname: 'Dataset 4', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '5', nickname: 'Dataset 5', created_time:"2022-10-10T19:12:44.257372" },
    { directory_id: '6', nickname: 'Dataset 6', created_time:"2022-10-10T19:12:44.257372" },
  ],
};