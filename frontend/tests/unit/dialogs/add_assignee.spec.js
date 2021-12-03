import { shallowMount } from "@vue/test-utils";
import add_assignee from "@/components/dialogs/add_assignee.vue";

describe("add_assignee.vue", () => {
  it("Does not show anything if the dialog is hidden", () => {
    const wrapper = shallowMount(add_assignee, {
      propsData: {
        dialog: false
      }
    });
    expect(wrapper.findAll("v-dialog").length).toBe(0);
  });
});
