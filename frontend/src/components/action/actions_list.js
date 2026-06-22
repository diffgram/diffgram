// An array of action template objects, each representing a possible action in a workflow.
// The 'ACTION_TEMPLATE_LIST' is an array of objects, where each object is a template for an action.
// These templates contain information about the action's trigger type, icon, kind, title, description,
// preview, and node properties.
export const ACTION_TEMPLATE_LIST = [
  // An action template object with the following properties:
  // - is_trigger: true, indicating that this action is a trigger action.
  // - icon: 'mdi-folder-arrow-up', the icon for this action.
  // - kind: 'file_upload', the kind of action this is.
  // - title: 'On File Uploaded', the title of the action.
  // - description: 'When a file is uploaded', a description of what the action does.
  {
    is_trigger: true,
    icon: 'mdi-folder-arrow-up',
    kind: 'file_upload',
    title: 'On File Uploaded',
    description: 'When a file is uploaded',
  },
  // Another action template object with similar properties as the previous one,
  // but with additional preview and node properties.
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
  // More action template objects follow, each with their own unique properties and descriptions.
];
