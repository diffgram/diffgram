import { shallowMount, mount } from "@vue/test-utils";
import is_complete from "@/components/dialogs/review_dialog.vue";
import Vuetify from "vuetify";
const vuetify = new Vuetify();

describe("review_dialog.vue", () => {
  it("Does not show anything if the dialog is hidden", () => {
    const wrapper = shallowMount(is_complete, {
      propsData: {
        dialog: false
      },
      vuetify
    });
    expect(wrapper.findAll("v-dialog").length).toBe(0);
  });

  it("Does show dialog if the dialog is true", () => {
    const wrapper = shallowMount(is_complete, {
      propsData: {
        dialog: true
      },
      vuetify
    });
    expect(wrapper.findAll("[data-cy='review_dialog']").length).toBe(1);
  });

  it("Emits on_task_action event on click cancel", async () => {
    const wrapper = mount(is_complete, {
      propsData: {
        dialog: true
      },
      vuetify
    });
    wrapper.find("#review-dialog-cancel").trigger("click");
    expect(wrapper.emitted().on_task_action).toBeTruthy();
  });

  it("Emits complete event on click submit", async () => {
    const wrapper = mount(is_complete, {
      propsData: {
        dialog: true
      },
      vuetify
    });
    wrapper.find("#review-dialog-submit").trigger("click");
    await wrapper.vm.$nextTick();
    expect(wrapper.emitted().complete).toBeTruthy();
  });
});
