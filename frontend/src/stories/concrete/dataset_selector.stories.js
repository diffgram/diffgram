import dataset_selector from "../../components/concrete/dataset/dataset_selector.vue";

const project_string_id = 'storybook-mock'

let dataset_list = [
  { 
    directory_id: 1, 
    nickname: 'Default', 
    created_time:"2022-10-10T19:12:44.257372" 
  },
  { 
    directory_id: 2, 
    nickname: 'My second dataset', 
    created_time:"2022-10-10T19:12:44.257372" 
  }
]

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

          const new_dataset = {
            id: Math.floor(Math.random() * 100),
            nickname: request_body.nickname,
            created_time: (new Date()).toISOString()
          }

          return {
              log: {
                success: true,
              },
              new_directory: new_dataset
          }
        }
      },
      {
        url: `/api/v1/project/${project_string_id}/directory/update`,
        method: 'POST',
        status: 200,
        response: (request) => {
          const request_body = JSON.parse(request.body)

          const updated_datasets = [...dataset_list].map(dataset => {
            if (dataset.directory_id === request_body.directory_id) {
              dataset.nickname = request_body.nickname
            }

            return dataset
          })

          dataset_list = updated_datasets

          return {
              log: {
                success: true,
              },
              project: {
                directory_list: updated_datasets
              }
          }
        }
      },
      {
        url: `/api/v1/project/${project_string_id}/directory/list`,
        method: 'POST',
        status: 200,
        response: (request) => {
          const request_body = JSON.parse(request.body)

          const dataset_to_return = [...dataset_list].filter(dataset => {
            let matches_from = true;
            let matches_to = true;
            let nickname_match = true;

            const dataset_creation = new Date(dataset.created_time)

            if (request_body.date_from) {
              const date_from_object = new Date(request_body.date_from)

              matches_from = dataset_creation >= date_from_object
            }

            if (request_body.date_to) {
              const date_to_object = new Date(request_body.date_to)

              matches_to = dataset_creation <= date_to_object
            }

            if (request_body.nickname) {
              nickname_match = dataset.nickname.toLowerCase().includes(request_body.nickname.toLowerCase())
            }

            return matches_from && matches_to && nickname_match
          })

          return {
              log: {
                success: true,
              },
              directory_list: dataset_to_return
          }
        }
      },
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
  set_from_id: 1,
  dataset_list: dataset_list,
};

export const ViewOnly = (args, { argTypes }) => ({
  components: {
    dataset_selector,
  },
  props: Object.keys(argTypes),
  template: '<dataset_selector v-bind="$props" />',
});
ViewOnly.args = {
  project_string_id,
  set_from_id: 1,
  view_only_mode: true,
  dataset_list: dataset_list,
};

export const WithUpdate = (args, { argTypes }) => ({
  components: {
    dataset_selector,
  },
  props: Object.keys(argTypes),
  template: '<dataset_selector v-bind="$props" />',
});
WithUpdate.args = {
  project_string_id,
  set_from_id: 1,
  show_update: true,
  dataset_list: dataset_list,
};

export const WithAddNew = (args, { argTypes }) => ({
  components: {
    dataset_selector,
  },
  props: Object.keys(argTypes),
  template: '<dataset_selector v-bind="$props" />',
});
WithAddNew.args = {
  project_string_id,
  set_from_id: 1,
  show_new: true,
  dataset_list: dataset_list,
};

export const SelectMultiple = (args, { argTypes }) => ({
  components: {
    dataset_selector,
  },
  props: Object.keys(argTypes),
  template: '<dataset_selector v-bind="$props" />',
});
SelectMultiple.args = {
  project_string_id,
  multiple: true,
  dataset_list: dataset_list,
};
