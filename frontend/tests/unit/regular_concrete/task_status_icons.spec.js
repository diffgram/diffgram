import { shallowMount } from "@vue/test-utils";
import task_status_icons from "@/components/regular_concrete/task_status_icons.vue";

describe("task_status_icons.vue", () => {
  it("Renders complete icons when the status is complete", () => {
    const wrapper = shallowMount(task_status_icons, {
      propsData: {
        status: "complete"
      }
    });
    expect(wrapper.html()).toContain('tooltip_message="Complete"');
    expect(wrapper.html()).toContain('icon="mdi-check"');
    expect(wrapper.html()).toContain('color="green"');
  });

  it("Renders available icons when the status is available", () => {
    const wrapper = shallowMount(task_status_icons, {
      propsData: {
        status: "available"
      }
    });
    expect(wrapper.html()).toContain('tooltip_message="Available"');
    expect(wrapper.html()).toContain('icon="mdi-inbox"');
    expect(wrapper.html()).toContain('color="primary"');
  });

  it("Renders in progress icons when the status is in_progress", () => {
    const wrapper = shallowMount(task_status_icons, {
      propsData: {
        status: "in_progress"
      }
    });
    expect(wrapper.html()).toContain('tooltip_message="In Progress"');
    expect(wrapper.html()).toContain('icon="mdi-account-clock-outline"');
    expect(wrapper.html()).toContain('color="primary"');
  });

  it("Renders in review icons when the status is review_requested", () => {
    const wrapper = shallowMount(task_status_icons, {
      propsData: {
        status: "review_requested"
      }
    });
    expect(wrapper.html()).toContain('tooltip_message="In review"');
    expect(wrapper.html()).toContain('icon="mdi-archive-eye-outline"');
    expect(wrapper.html()).toContain('color="primary"');
  });

  it("Renders require changes icons when the status is requires_changes", () => {
    const wrapper = shallowMount(task_status_icons, {
      propsData: {
        status: "requires_changes"
      }
    });
    expect(wrapper.html()).toContain('tooltip_message="Requires changes"');
    expect(wrapper.html()).toContain('icon="mdi-clipboard-alert-outline"');
    expect(wrapper.html()).toContain('color="red"');
  });
});
