
export function addQueriesToLocation (queries: object) {
  /* Example usage
     * this.$addQueriesToLocation({'frame': frame_value});
     * 
     * where frame will be used as the name
     * and the value of frame will be the value passed eg
     * let frame = 1
     * this.$addQueriesToLocation({frame});
     * yields adding this to the route:
     * ?frame=1  (existing queries will be maintained, and the page will not refresh)
   *
   * Cautions on internal workings
   *   1) params vs queries  (some ideas are for params which are different context)
   *   2) Can't seem to use this.$route.query because it doesn't update
   *
   * Goal:
    *  is that we can pass an updated query ,
    *  and if it exists it replaces the existing key
    *  and it if doesn't exist it will add it (while preserving existing ones!)
    *
    * Context of wanting to preserve existing queries by default
    * https://stackoverflow.com/a/56691111  (scroll lots of answers)
    * 
    * Main issue is that, at least for current annotation core setup, this.$route.push causes a reload (which we don't want)
    * And in order to avoid duplicating keys, we need some notation of parsing the existing
    * string to an object, and then re pushing it. Probably a cleaner way to do it but
    * was nature of trying to write it here.
    * 
   * Current state
   *  This setup now seems to work
   *  but with the same cavet as prior that 'Vue Router don't know that url has changed, so it doesn't reflect url after pushState'
   *  It so far appears like there isn't a clearly better work around in this specific context
   *
   *  Example use case being called from various places
   *  http://127.0.0.1:8085/task/19647?frame=20&instance=1360664&attribute_group=315
   *  Keep in mind that this can change multiple times too
   *  eg going to next frame changes the frame,
   *  and then naturally the instance will change too...
   *
   *  Small? issue: Order is not preserved in some cases. in those cases the url change looks kinda awkward in some cases
   *
   *   Another option perhaps would be to just dump all the keys known and set values to null
   *   but that makes the url kind of ugly for more base cases... plus then have to worry about tracking that...
   *   where as this way any process can add a key as needed could be relevant for other areas too, eg
   *   jumping to a specific label, or place in the task template creation or something?
   */

    let existing_queries = convert_query_string_to_object()
    let url_query_addition = update_and_add_new_queries(queries, existing_queries)
    let string_existing_queries = convert_existing_queries_to_string(existing_queries)
    
    let new_desired_url = this.$route.path + '?' + string_existing_queries + url_query_addition

    history.pushState(
      {},
      null,
      new_desired_url
    )
}

function url_encoder(key, value) {
  key = encodeURIComponent(key)
  value = encodeURIComponent(value)
  if (key == 'undefined' || value == 'undefined') {
    return ""
  }
  return key + "=" + value + "&"
}

function update_and_add_new_queries(
        queries: object,
        existing_queries: object) {

  let url_query_addition = ''
  for (let [key, value] of Object.entries(queries)) {
    url_query_addition += url_encoder(key, value)
    if (key in existing_queries) {
      delete existing_queries[key]
    }
  }
  return url_query_addition
}

function convert_existing_queries_to_string(
          existing_queries: object) {
    // this could probably be refactored with update_and_add_new_queries()...
    //console.log(existing_queries)
    let string_existing_queries = ''
    for (let [key, value] of Object.entries(existing_queries)) {
       string_existing_queries += url_encoder(key, value)
    }
    return string_existing_queries
}

function convert_query_string_to_object() {
    var query_string = window.location.search.substring(1)      //  this.$route.fullPath path doesn't update either
    let new_query_object = {}
    var vars = query_string.split('&')
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split('=')
        new_query_object[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1])
    }
    return new_query_object
}


export function format_money(value) {
      return '$' + (value / 100).toLocaleString('en-US', {
        maximumFractionDigits: 2,
        minimumFractionDigits: 2
      })
    }
