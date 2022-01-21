import * as SequenceUpdateHelpers from "../../../../src/components/annotation/utils/SequenceUpdateHelpers";

describe("Test SequenceUpdateHelpers.ts", () => {

  beforeEach(() => {

  });

  it("Correctly calls populate_empty_sequence_ids()", () => {
    let instance_list = [
      {
        id: 1,
        sequence_id: 1,
        number: 1,
        label_file_id: 1
      },
      {
        id: 2,
        number: 2,
        sequence_id: undefined,
        label_file_id: 2
      },
      {
        id: 3,
        number: 2,
        sequence_id: undefined,
        label_file_id: 2
      },
      {
        id: 4,
        number: 3,
        sequence_id: undefined,
        label_file_id: 3
      },
      {
        id: 5,
        number: 1,
        sequence_id: undefined,
        label_file_id: 3
      },

    ]
    let sequence_list = [
      {
        id: 1,
        number: 1,
        label_file_id: 1
      },
      {
        id: 2,
        number: 2,
        label_file_id: 2
      },
      {
        id: 3,
        number: 1,
        label_file_id: 3
      },
      {
        id: 4,
        number: 3,
        label_file_id: 3
      }
    ]
    SequenceUpdateHelpers.populate_empty_sequence_ids(
      instance_list,
      sequence_list
    )
    expect(instance_list[0].sequence_id).toEqual(1)
    expect(instance_list[1].sequence_id).toEqual(2)
    expect(instance_list[2].sequence_id).toEqual(2)
    expect(instance_list[3].sequence_id).toEqual(4)
    expect(instance_list[4].sequence_id).toEqual(3)
  });


});
