import tooltip_button from '../components/regular/tooltip_button.vue';

export default {
  title: 'Regular/TooltipButton',
  component: tooltip_button
};

export const TooltipButton = (args) => ({
  components: { 
    tooltip_button 
  },
  template: '<tooltip_button v-bind="$props" />'
});

