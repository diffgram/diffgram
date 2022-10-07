import tooltip_button from "../components/regular/tooltip_button.vue";

export default {
  title: "Regular/TooltipButton",
  component: tooltip_button,
};

export const TooltipButton = (args, { argTypes }) => ({
  components: {
    tooltip_button,
  },
  props: Object.keys(argTypes),
  template: '<tooltip_button v-bind="$props" />',
});
