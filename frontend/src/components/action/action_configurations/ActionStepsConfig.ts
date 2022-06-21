const default_steps_config = {
  triggers: {
    header_title: 'When',
    number: 1,
    title: 'Configure Step Trigger',
    message: 'Trigger are events that will start the execution of this action.',
    hide: false
  },
  pre_conditions: {
    header_title: 'Check Conditions',
    number: 2,
    title: 'Configure Conditions',
    message: 'Additional conditions to checks for the execution of the step..',
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

interface Step {
  name: string;
  number: number;
  title: string;
  message: string;
  hide: boolean;
}

export default class ActionStepsConfig {
  private default_steps: Object = { ...default_steps_config };
  private additional_steps: Object = {};

  constructor(new_steps: Object = {}) {
    if (new_steps) {
      this.additional_steps = new_steps;
    }
  }

  private get_non_hiden_steps(steps_object: Object): Object {
    const steps_to_return = {};

    const keys = Object.keys(steps_object)
    keys.map(key => {
      if (!steps_object[key].hide) steps_to_return[key] = steps_object[key]
    })

    return steps_to_return
  }

  public hide_step(step_name: string): void {
    if (this.default_steps[step_name]) this.default_steps[step_name].hide = true
    if (this.additional_steps[step_name]) this.additional_steps[step_name].hide = true
  }

  public show_step(step_name: string): void {
    if (this.default_steps[step_name]) this.default_steps[step_name].hide = false
    if (this.additional_steps[step_name]) this.additional_steps[step_name].hide = false
  }

  public update_step_number(step_name: string, new_step_number: number): void {
    if (this.default_steps[step_name]) {
      this.default_steps[step_name].number = new_step_number
      this.default_steps[step_name].important = true
    }
    
    if (this.additional_steps[step_name]) {
      this.additional_steps[step_name].number = new_step_number
      this.additional_steps[step_name].important = true
    }
  }

  public add_step(step: Step): void {
    const step_name = step.name;
    if (
      !this.default_steps[step_name] && 
      !this.additional_steps[step_name]
    ) this.additional_steps[step_name] = { ...step }
  }

  public generate(): Object {
    const non_hidden_default_steps = this.get_non_hiden_steps({ ...this.default_steps })
    const non_hidden_additionsl_steps = this.get_non_hiden_steps({ ...this.additional_steps })

    const all_steps = { ...non_hidden_default_steps, ...non_hidden_additionsl_steps }

    return all_steps
  }
}

