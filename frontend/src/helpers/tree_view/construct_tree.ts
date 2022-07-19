import {Node} from "../interfaces/TreeNode";

let root_path: Array<any> = [];

// export const find_all_parents = (id, array, global_tracker = []) => {
//   const local_tracker = []
//   const current_node = array.find(node => node.get_id() === id)

//   let working_node = current_node

//   const nodes_to_return = []
//   nodes_to_return.push(current_node)
//   local_tracker.push(current_node.get_id());

//   if (
//     !current_node.get_parent() || 
//     local_tracker.includes(current_node.get_parent()) ||
//     global_tracker.includes(current_node.get_parent())
//   ) {
//     return { nodes_to_return, local_tracker }
//   };

//   let checker_node = array.find(node => {
//     return node.get_id() === working_node.get_parent()
//   })

//   function find_parent() {
//       if (
//         local_tracker.includes(current_node.get_parent()) ||
//         global_tracker.includes(current_node.get_parent())
//       ) return { nodes_to_return, local_tracker }
  
//       checker_node = array.find(node => {
//         return node.get_id() === working_node.get_parent()
//       })
//       console.log("here")
      
//       nodes_to_return.push(checker_node)
//       local_tracker.push(checker_node.get_id())
//       working_node = checker_node
//       setTimeout(find_parent, 0)
//   }

//   find_parent()

//   return { nodes_to_return, local_tracker }
// }

export const find_all_parents = (id, array, global_tracker) => {
  const local_tracker = []
  const current_node = array.find(node => node.get_id() === id)

  let working_node = current_node

  const nodes_to_return = []
  nodes_to_return.push(current_node)
  local_tracker.push(current_node.get_id());

  if (
      !current_node.get_parent() || 
      local_tracker.includes(current_node.get_parent()) || 
      global_tracker.includes(current_node.get_parent())
    ) return { nodes_to_return, local_tracker }

  while(working_node && working_node.get_parent()) {
    const checker_node = array.find(node => {
      return node.get_id() === working_node.get_parent()
    })
    nodes_to_return.push(checker_node)
    local_tracker.push(checker_node.get_id())
    working_node = checker_node
  }

  return {nodes_to_return, local_tracker}
}

export const tree_parents = (id, array, global_tracker = []) => {
  return new Promise((resolve, reject) => {
    const result = find_all_parents(id, array, global_tracker)
    resolve(result)
  })
}

export const find_all_relatives = (id, array) => {
  const related_nodes = []
  const related_indexes = array
    .filter(item => item.get_parent() === id)
    .map(item => {
      related_nodes.push(item)
      return item.get_id()
    })

  related_indexes.push(id)
  related_nodes.push(array.find(node => node.id === id))
  let has_more = true;

  while (has_more) {
    const has_more_relatives = array.filter(item =>
      related_indexes.includes(item.get_parent()) && !related_indexes.includes(item.get_id())
    )

    if (has_more_relatives.length === 0) {
      has_more = false
      return {related_indexes, related_nodes}
    }
    has_more_relatives.map(item => related_indexes.push(item.get_id()))
    has_more_relatives.map(item => related_nodes.push(item))
  }

  return {related_indexes, related_nodes}
}

export const build_path = (array: Array<any>, parent_id, path) => {
  array.map((item, index) => {
    const copy_path = [...path]
    if (item.id === parent_id) {
      copy_path.push(index)
      root_path = copy_path
      return
    }
    copy_path.push(index)
    copy_path.push("children")
    build_path(item.children, parent_id, copy_path)
  })

  return root_path
}

export const construct_tree = (node_list: Array<Node>): Array<any> => {
    root_path = []
    const node_list_working_copy = [...node_list]
    const node_wait_list = []
    const tree = [];
    const check_list = [];

    node_list_working_copy.map(item => {
        const render_item = item.get_render_data()
        if (!render_item.parent) {
            tree.push(render_item)
        } else {
            node_wait_list.push(render_item)
        }
    })

    while (node_wait_list.length !== 0) {
        root_path = []
        const render_item = node_wait_list.shift()
        const returned_path = build_path(tree, render_item.parent, [])
        let track_item: any = tree
        root_path.map(q_item => {
            track_item = track_item[q_item]
        })
        if (returned_path && returned_path.length !== 0 && track_item) {
            track_item.children.push(render_item)
        } else if (node_wait_list.find(item => item.id === render_item.parent)) {
            node_wait_list.push(render_item)
        } else {
          check_list.push(render_item)
        }
    }

    return tree
}
