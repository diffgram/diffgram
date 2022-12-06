

export type AttributeGroup = {
  id: number
  display_name: string
  prompt: string
  schema_id: number
}

export type AttributeGroupMap = {
  [key: number]: AttributeGroup
}
