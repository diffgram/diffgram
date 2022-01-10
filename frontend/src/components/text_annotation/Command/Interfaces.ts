export interface TextInstance {
    id: number;
    type: string;
    sentense_index: number;
    label: any;
    creation_ref_id: string;
}

export interface TextLabelInstanse extends TextInstance {
    labelItems: DrawLabelItem[];
}

export interface TextRelationInstance extends TextInstance {
    relationItems: DrawRelationItem[];
    start_marker: MarkerPosition;
    end_marker: MarkerPosition;
    start_label: number;
    end_label: number;
}

export interface DrawLabelItem {
    x: number;
    y: number;
    width: number;
}

export interface DrawRelationItem {
    M1: number;
    M2: number;
    H: number;
}

export interface MarkerPosition {
    x: number;
    y: number;
}

