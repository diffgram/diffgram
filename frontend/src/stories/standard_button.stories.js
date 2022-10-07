import standard_button from "../components/base/standard_button.vue";

export default {
  title: "Base/StandardButton",
  component: standard_button,
};

export const Default = (args, { argTypes }) => ({
  components: {
    standard_button,
  },
  props: Object.keys(argTypes),
  template: '<standard_button v-bind="$props" />',
});

export const ChangeIcon = (args, { argTypes }) => ({
  components: {
    standard_button,
  },
  props: Object.keys(argTypes),
  template: '<standard_button v-bind="$props" />',
  title: 'MyComponent',
});
ChangeIcon.args = {
  icon: "mdi-content-copy"
};

export const Primary = (args, { argTypes }) => ({
  components: {
    standard_button,
  },
  props: Object.keys(argTypes),
  template: '<standard_button v-bind="$props" />',
});
Primary.args = {
  button_message: "Primary",
  button_color: "primary",
  icon: "",
};

export const PrimaryWithTooltip = (args, { argTypes }) => ({
  components: {
    standard_button,
  },
  props: Object.keys(argTypes),
  template: '<standard_button v-bind="$props" />',
});
PrimaryWithTooltip.args = {
  button_message: "Primary",
  tooltip_message: "Primary button tooltip message",
  button_color: "primary",
  icon: "",
};

export const Text = (args, { argTypes }) => ({
  components: {
    standard_button,
  },
  props: Object.keys(argTypes),
  template: '<standard_button v-bind="$props" />',
});
Text.args = {
  text_style: true,
  button_message: "Text style button",
  icon: "",
};
