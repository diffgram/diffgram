import tooltip_button from '../components/regular/tooltip_button.vue';
import store from '../store'

export default {
  title: 'Regular/tooltip_button',
  component: tooltip_button,
  argTypes: {
    backgroundColor: { control: 'color' },
    size: {
      control: { type: 'select' },
    },
  },
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { tooltip_button },
  template: '<tooltip_button v-bind="$props" />',
  store: store
});

export const Primary = Template.bind({});
Primary.args = {
  primary: true,
  label: 'Button',
};
