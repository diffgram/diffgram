

export const default_steps_config = {
  triggers: {
    header_title: 'When',
    number: 1,
    title: 'Configure Step Trigger',
    message: 'Trigger are events that will start the execution of this action.',
    hide: false
  },
  pre_conditions: {
    header_title: 'Execution Conditions',
    number: 2,
    title: 'Configure Execution Conditions',
    message: 'Additional conditions to check for the execution of the step..',
    hide: false
  },
  action_config: {
    header_title: 'Do',
    number: 3,
    title: 'Action Step Configuration',
    message: 'Provide the data for the action step  execution.',
    hide: false
  },
  completion_trigger: {
    header_title: 'Next',
    number: 4,
    title: 'Completes When: ',
    message: 'Provide the condition that will make this step complete.',
    hide: false
  },
}
