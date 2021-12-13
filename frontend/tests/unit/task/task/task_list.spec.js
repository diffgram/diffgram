import { shallowMount, createLocalVue } from "@vue/test-utils";
import task_list from "@/components/task/task/task_list.vue";
import Vuex from "vuex";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("task_list.vue", () => {
  let props;

  beforeEach(() => {
    props = {
      mocks: {
        $store: {
          state: {
            job: {
              current: {
                id: 1
              }
            }
          }
        }
      }
    };
  });

  it("Render task_list component correctly", () => {
    const wrapper = shallowMount(task_list, props, localVue);
    expect(wrapper.findAll("[data-cy='task_list_container']").length).toBe(1);
  });

  it("Should open dialog correctly", () => {
    const wrapper = shallowMount(task_list, props, localVue);
    expect(wrapper.vm.$data.task_assign_dialog_open).toBe(false);
    expect(wrapper.vm.$data.task_to_assign).toBe(null);
    expect(wrapper.vm.$data.task_assign_dialog_type).toBe(null);
    wrapper.vm.on_assign_dialog_open(1, "assignee");
    expect(wrapper.vm.$data.task_assign_dialog_open).toBe(true);
    expect(wrapper.vm.$data.task_to_assign).toBe(1);
    expect(wrapper.vm.$data.task_assign_dialog_type).toBe("assignee");
  });

  it("Should open batch dialog correctly", () => {
    const wrapper = shallowMount(task_list, props, localVue);
    expect(wrapper.vm.$data.task_assign_dialog_open).toBe(false);
    expect(wrapper.vm.$data.task_assign_dialog_type).toBe(null);
    expect(wrapper.vm.$data.task_assign_batch).toBe(false);
    wrapper.vm.on_batch_assign_dialog_open("assignee");
    expect(wrapper.vm.$data.task_assign_dialog_open).toBe(true);
    expect(wrapper.vm.$data.task_assign_dialog_type).toBe("assignee");
    expect(wrapper.vm.$data.task_assign_batch).toBe(true);
  });

  it("Should close dialog correctly", () => {
    const wrapper = shallowMount(task_list, props, localVue);
    wrapper.vm.$data.task_assign_dialog_open = true;
    wrapper.vm.$data.task_to_assign = 1;
    wrapper.vm.$data.task_assign_dialog_type = "assignee";
    wrapper.vm.$data.task_assign_dialog_loading = true;
    wrapper.vm.$data.task_assign_batch = true;
    wrapper.vm.on_assign_dialog_close();
    expect(wrapper.vm.$data.task_assign_dialog_open).toBe(false);
    expect(wrapper.vm.$data.task_to_assign).toBe(null);
    expect(wrapper.vm.$data.task_assign_dialog_type).toBe(null);
    expect(wrapper.vm.$data.task_assign_dialog_loading).toBe(false);
    expect(wrapper.vm.$data.task_assign_batch).toBe(false);
  });
});
