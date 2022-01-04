export interface TextInstance {
    id: number;
    type: string;
    sentense_index: number;
    label: any;
}

export interface TextLabelInstanse extends TextInstance {
    x: number;
    y: number;
    width: number;
}

export interface TextRelationInstance extends TextInstance {
    M1: number;
    M2: number;
    H: number;
    start_label: number;
    end_label: number;

}