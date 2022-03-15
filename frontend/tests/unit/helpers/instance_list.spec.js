import InstanceList from "../../../src/helpers/instance_list";
import TestInstance from "./TestCalsses/TestInstances";

describe("Testing InstanceList", () => {
    let instance_list;

    beforeEach(() => {
        instance_list = new InstanceList();
    });

    it("Get method return empty array", () => {
        expect(instance_list.get()).toEqual([])
    })

    it("Get_all method return empty array", () => {
        expect(instance_list.get_all()).toEqual([])
    })

    it("Pushes new command to the instance list", () => {
        const instance = new TestInstance(0, 'text_token')
        instance_list.push([instance])

        expect(instance_list.get().length).toEqual(1)
        expect(instance_list.get()[0]).toEqual(instance)

        expect(instance_list.get_all().length).toEqual(1)
        expect(instance_list.get_all()[0]).toEqual(instance)
    })

    it("Pushes soft deleted instance", () => {
        const instance = new TestInstance(0, 'text_token', true)
        instance_list.push([instance])

        expect(instance_list.get().length).toEqual(0)

        expect(instance_list.get_all().length).toEqual(1)
        expect(instance_list.get_all()[0]).toEqual(instance)
    })

    it("Replcaes instance", () => {
        const initial_instance = new TestInstance(0, 'text_token')
        instance_list.push([initial_instance])

        expect(instance_list.get().length).toEqual(1)
        expect(instance_list.get()[0]).toEqual(initial_instance)

        expect(instance_list.get_all().length).toEqual(1)
        expect(instance_list.get_all()[0]).toEqual(initial_instance)

        const new_instance = new TestInstance(0, 'relation', true)
        instance_list.replace(new_instance, 0)

        expect(instance_list.get().length).toEqual(0)

        expect(instance_list.get_all().length).toEqual(1)
        expect(instance_list.get_all()[0]).toEqual(new_instance)
    })

    it("Constructor initializes correctly text_token instance", () => {
        const insatnces = [{
            id: 0,
            label_file: {}, 
            type: "text_token",
            creation_ref_id: "ref",
            start_token: 0, 
            end_token: 0
        }]
        const instance_list = new InstanceList(insatnces)
        
        expect(instance_list.get().length).toEqual(1)
    })

    it("Constructor initializes correctly relation instance", () => {
        const insatnces = [{
            id: 0,
            label_file: {}, 
            type: "relation",
            creation_ref_id: "ref",
            from_instance_id: 0, 
            to_instance_id: 0, 
            soft_delete: false
        }]
        const instance_list = new InstanceList(insatnces)
        
        expect(instance_list.get().length).toEqual(1)
    })

    it("Constructor does not initialize unknown instance type instance", () => {
        const insatnces = [{
            id: 0,
            label_file: {}, 
            type: "other",
            creation_ref_id: "ref",
            from_instance_id: 0, 
            to_instance_id: 0, 
            soft_delete: false
        }]
        const instance_list = new InstanceList(insatnces)
        
        expect(instance_list.get().length).toEqual(0)
    })
})
