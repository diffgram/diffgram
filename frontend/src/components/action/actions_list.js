export const ACTION_TEMPLATE_LIST = [
  {
    is_trigger: true,
    icon: 'mdi-folder-arrow-up',
    kind: 'file_upload',
    title: 'On File Uploaded',
    description: 'When a file is uploaded',
  },
  {
    is_trigger: true,
    icon: 'mdi-folder-arrow-up',
    kind: 'file_upload',
    preview: {
      title: 'Receive Data from Pre-Label',
    },
    node: {
      title: 'On File Uploaded',
      description: 'When a file is uploaded',
    },
  },
  {
    is_trigger: true,
    icon: 'mdi-folder-arrow-up',
    kind: 'file_upload',
    preview: {
      title: 'Receive/Wait for Start from External Process',
    },
    node: {
      title: 'Receive/Wait forStart from External Process',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-folder-arrow-up',
    kind: 'file_upload',
    preview: {
      title: 'Generate Export',
    },
    node: {
      title: 'Generate Export',
      description: '...........',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-folder-arrow-up',
    kind: 'file_upload',
    preview: {
      title: 'Push Data to a Bucket',
    },
    node: {
      title: 'Push Data to a Bucket',
      description: '...........',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-folder-arrow-up',
    kind: 'file_upload',
    preview: {
      title: 'Run Custom Code',
    },
    node: {
      title: 'Run Custom Code',
      description: '...........',
    },
  },
  {
    is_trigger: true,
    icon: 'mdi-folder-arrow-up',
    kind: 'manual',
    preview: {
      title: 'Manual Trigger',
    },
    node: {
      title: 'On Manual Trigger',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-checkbox-multiple-marked-outline',
    kind: 'create_tasks',
    preview: {
      title: 'Human Tasks',
    },
    node: {
      title: 'Human Tasks',
      description: 'Human Tasks',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-brain',
    kind: 'run_inferences',
    preview: {
      title: 'Run Pre-Label',
    },
    node: {
      title: 'Run Pre-Label',
      description: 'Run model and add labels to the file',
    },
  },
  {
    is_trigger: false,
    kind: 'webhook',
    icon: 'mdi-code-braces-box',
    preview: {
      title: 'POST to Webhook',
    },
    node: {
      title: 'POST to Webhook',
      description: 'Send data to a given webhook.',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Filter Data',
    },
    node: {
      title: 'Filter Data',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Start Training',
    },
    node: {
      title: 'Start Training',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Train Azure Model',
    },
    node: {
      title: 'Train Azure Model',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Validate Model Performance',
    },
    node: {
      title: 'Validate Model Performance',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Create an Issue If',
    },
    node: {
      title: 'Create an Issue If',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Wait until all issues are resolved',
    },
    node: {
      title: 'Wait until all issues are resolved',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Condition on a class',
    },
    node: {
      title: 'Condition on a class',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Alert / Email',
    },
    node: {
      title: 'Alert / Email',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Task Milestone Reached',
    },
    node: {
      title: 'Task Milestone Reached',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Loop Back to a Step',
    },
    node: {
      title: 'Loop Back to a Step',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Deploy Dataset',
    },
    node: {
      title: 'Deploy Dataset',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Query Data',
    },
    node: {
      title: 'Query Data',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Visualize Data',
    },
    node: {
      title: 'Visualize Data',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Visualize Human Performance',
    },
    node: {
      title: 'Visualize Human Performance',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Show Customized (UI Schema) Studio View',
    },
    node: {
      title: 'Show Customized (UI Schema) Studio View',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Show Customized (UI Schema) Data Explorer View',
    },
    node: {
      title: 'Show Customized (UI Schema) Data Explorer View',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Visualize Model Performance',
    },
    node: {
      title: 'Visualize Model Performance',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Move/Copy Data',
    },
    node: {
      title: 'Move/Copy Data',
      description: '...',
    },
  },
  {
    is_trigger: false,
    icon: 'mdi-filter',
    kind: 'filter',
    preview: {
      title: 'Stop Until / Human Supervision Control Point',
    },
    node: {
      title: 'Stop Until / Human Supervision Control Point',
      description: '...',
    },
  },
]
