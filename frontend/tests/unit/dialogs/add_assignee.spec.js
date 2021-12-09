import { shallowMount } from "@vue/test-utils";
import add_assignee from "@/components/dialogs/add_assignee.vue";

describe("add_assignee.vue", () => {
  let props;

  beforeEach(() => {
    props = {
      propsData: {
        dialog: true
      },
      mocks: {
        $store: {
          state: {
            project: {
              current: {
                member_list: [1, 2]
              }
            }
          }
        }
      }
    };
  });

  it("Does not show anything if the dialog is hidden", () => {
    props.propsData.dialog = false;
    const wrapper = shallowMount(add_assignee, props);

    expect(wrapper.findAll("v-dialog").length).toBe(0);
  });

  it("Show dialog when it's open", () => {
    const wrapper = shallowMount(add_assignee, props);

    expect(wrapper.findAll("v-dialog").length).toBe(1);
  });

  it("Emits assign event when submit button is pressed", () => {
    const wrapper = shallowMount(add_assignee, props);
    wrapper.find("#review-dialog-submit").trigger("click");
    expect(wrapper.emitted().assign).toBeTruthy();
  });

  it("Emits close event when cancel button is pressed", () => {
    const wrapper = shallowMount(add_assignee, props);
    wrapper.find("#review-dialog-cancel").trigger("click");
    expect(wrapper.emitted().close).toBeTruthy();
  });
});
