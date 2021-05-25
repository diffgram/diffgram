import {v4 as uuidv4 } from 'uuid'


export class UserScript {
  public error_construction = null
  public error_runtime = null
  public error_line = null
  public error_char = null
  public logMessages = []
  private userscript_namespace_string = "__userscript_namespace_diffgram"
  private desired_context = null

  public status_loaded_scripts = false
  public status_loaded_watchers = false

  private prior_content = null
  private prior_parsed_function = null

  public running = false

  private time_start = null
  private time_end = null
  private run_time = null
  private loading_scripts = false

  private watch_functions = {
      'create_instance' : []
    }


  // TODO consider storing attributes in userscript
  // instead of "generic" Js object.

  constructor() {
      // this.test_build_and_register_watcher()
  }

  public new_userscript(code=""): any {

    // Caution code mirror errors if "code" is undefiend

    let userscript = {}
    userscript.client_creation_ref_id = uuidv4();
    userscript.client_created_time = new Date().toISOString();
    userscript.name = "Untitled script";
    userscript.code = code
    userscript.archived = false
    userscript.is_visible = true
    userscript.is_public = false
    userscript.language = 'javascript'  // default
    userscript.use_instructions = null
    userscript.docs_link = null
    userscript.star_rating_cache = null
    userscript.external_src_list = [ ]
    return userscript

  }

  public copy_userscript(old_userscript): any {

    let userscript = {...old_userscript}
    userscript.external_src_list = [...old_userscript.external_src_list]

    // Values we expect to be different in copied version
    userscript.client_creation_ref_id = uuidv4();
    userscript.client_created_time = new Date().toISOString();
    userscript.name = "Copy of " + old_userscript.name
    userscript.is_public = false
    return userscript

  }


  public reset_shared(): any {

    this.watch_functions = {
      'create_instance' : []
    }
  }

  public parse_single_function(content, desired_context): any {

    let AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;


    // caution replace returns a new string NOT in place
    // g operator all instances https://www.digitalocean.com/community/tutorials/replace-all-instances-of-a-string-in-javascript
    // CAREFUL regular expression eg so can't do string + operator
    
    let class_special_word = 'diffgram'
    let reg_exp = new RegExp(class_special_word, 'g')

    let local_content = content.replace(
      reg_exp,
      desired_context)


    // TODO link to this specific component not yet defined
    //local_content = local_content.replace(/console.log/g, 'this.__userscript_console')
    //console.log("replaced", local_content)


    this.error_construction = null // reset error
    this.desired_context = desired_context

    var class_context = this

    // Catch errors during function def
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/AsyncFunction
    try {
      var new_function = new AsyncFunction(
        'data',
        local_content
      )
    }
    catch (error) {
      class_context.error_construction = error
      console.log(error)
      // It appears that there isn't a line number usually available
      // for construction type errors
    }

    if (class_context.error_construction) {
      return
    }

    // console.log(new_function)

    // catch errors at run time
    async function parsed_function(...data) {
      // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/rest_parameters
        try {
            //console.log(data)
            await new_function(data);
        } catch (error) {
            class_context.error_runtime = class_context.strip_desired_context_from_error(error.message)
            console.log(error)
            if (error.stack) {
              let error_line_and_char = class_context.get_line_number(error.stack)
              class_context.error_line = error_line_and_char[0]
              class_context.error_char = error_line_and_char[1]
            }
        } finally {
            //console.log('We do cleanup here');
        }
    }

    return parsed_function


  }

  private parse_high_level_into_functions(content, desired_context) {

    if (!content) { return }
    // TODO parse from watch dict first
    // do actual parser
    let starting_index = content.indexOf("data){");
    let watcher = content.slice(starting_index + 6)
    let ending_index = watcher.lastIndexOf("}");
    //let ending_index = watcher.indexOf("}");
    watcher = watcher.slice( 0 , ending_index)
    console.log("watcher string", watcher)

    this.build_and_register_watcher(watcher, desired_context)

  }

  private test_build_and_register_watcher(
      unparsed_string='console.log(data)',
      desired_context = "") {
    this.build_and_register_watcher(unparsed_string, desired_context)
    // then call create box

  }

  private async run (parsed_function) {
    this.running = true
    this.time_start = performance.now()

    await parsed_function()

    this.time_end = performance.now()
    this.run_time = Math.round(this.time_end - this.time_start)
    this.running = false
  }

  public async run_event(event){

    // future, may want to think about computation here
    // eg if there are no events "registered" to return by default

    let desired_function = this.watch_functions['create_instance'][0]
    if (!desired_function) { return }

    // this doesn't log as expected may be something with await/async

    this.running = true
    this.time_start = performance.now()

    console.log("event create_instance")
    await desired_function(event)

    this.time_end = performance.now()
    this.run_time = Math.round(this.time_end - this.time_start)
    this.running = false
  }


  private build_and_register_watcher(unparsed_string, desired_context) {

    this.status_loaded_watchers = false

    this.watch_functions['create_instance'] = [] // reset

    let parsed_function = this.parse_single_function(unparsed_string, desired_context)

    this.watch_functions['create_instance'].push(parsed_function)

    console.log(this.watch_functions['create_instance'])

    this.status_loaded_watchers = true

  }

  private build_and_run(content, desired_context){

    // runtime errors are reset here, build errors at parse
    this.error_runtime = null // reset error
    this.error_line = null
    this.error_char = null

    let allow_cache = true    // eg for debug
    let parsed_function

    if (allow_cache == true) {
      if (this.prior_content == content) {
        parsed_function = this.prior_parsed_function
        console.log("Used cached function")
      }
    }

    if (!parsed_function) {
      parsed_function = this.parse_single_function(content, desired_context)
    }

    // guards
    if (this.error_construction) {
      return
    }

    this.run(parsed_function)

    // cache
    this.prior_content = content
    this.prior_parsed_function = parsed_function
  }


  private strip_desired_context_from_error(error): string {
    /* Context of say calling a Diffgram function wrongly
     * eg this.function_may_exist() (from user)
     * (still not sure if we want to overload `this` or have like diffgram,
     * but either way the idea is the same)
     *
     * test by calling this.does_not_exist() expect
     * diffgram.points_to_instances is not a function
     */
    // invert the link we setup
    if (!error) { return error}

    let local_content = error.replace('document.querySelector(...).', '')

    let starting_index = this.desired_context.search("__vue__");
    let context_string = this.desired_context.slice(starting_index)
    let search = context_string // note just the first instance for now
    console.log(search)
    local_content = local_content.replace(search, 'diffgram')
    return local_content
  }

  private __userscript_console(): any {
    this.logMessages = [] // clear log by default for now
    // TODO may need something like JSON.stringify()
    this.logMessages.push.apply(this.logMessages, arguments);
  }

  public remove_old_add_new(allowed_scripts): any {

    let remove_result_bool = this.remove_userscripts_not_allowed(allowed_scripts)
    //console.log(remove_result_bool)

    this.add_script_multiple(allowed_scripts)

  }

  public remove_userscripts_not_allowed(allow_list): any {

    // temporary special exemption because removing and rebinding it later
    // leads to WASM / random errors
    // if many scripts aren't really designed to be added/removed we may
    // need a more robust solution here
    let local_allow_list = []
    if (allow_list) {
      local_allow_list = [...allow_list]
    }
    local_allow_list.push('https://docs.opencv.org/master/opencv.js')
    local_allow_list.push('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.2.0/dist/tf.min.js')

    let discovered_scripts_list = this.discover_all_scripts_not_in_list(
      local_allow_list)

    let result_bool = this.remove_script_multiple(discovered_scripts_list)
    //console.log('remove_userscripts_not_allowed', result_bool)

  }

  private discover_all_userscripts(): any {

    let discovered_scripts_list = []
    let existing_scripts_list = document.getElementsByTagName("script")

    for (let script of existing_scripts_list){
      if (script.title == this.userscript_namespace_string) {
        discovered_scripts_list.push(script)
      }
    }
    return discovered_scripts_list
  }


  private discover_all_scripts_not_in_list(allow_list): any {

    let discovered_scripts_list = []
    let existing_scripts_list = document.getElementsByTagName("script")
    //console.log(existing_scripts_list)

    for (let script of existing_scripts_list){
      if (script.title != this.userscript_namespace_string) {  // may be other scripts on page, isolate to userscript
        continue
      }

      if (allow_list &&
          !allow_list.includes(script.src)) {
        //console.log("discovered", script.title, script.src)
        discovered_scripts_list.push(script.src)
      }

    }

    //console.log("discovered_scripts_list", discovered_scripts_list)

    return discovered_scripts_list

  }

  private remove_script_multiple(script_url_list): any {
    if (!script_url_list){ return true}
    for (let script_url_string of script_url_list){
      if (!script_url_string) { continue }    // handle null cases
      let result = this.remove_script(script_url_string)
      console.log(result)
    }
    return true
  }

  private remove_script(script_url_string) : any {
    let object = document.getElementById(script_url_string)
    if (object) {
      object.remove()
      return true
    } else {
      return false
    }
  }

  public async add_script_multiple (script_url_list) : any{
    // assumes it will only add ones that don't exist
    /* assumes list is ordered as desired
     *
     * Will attempt to add at start of head
     * unless existing userscripts, then at end of existing ones
     *
     * design -> https://docs.google.com/document/d/1RFJMy0T8fI9B6he79V6mrwV2Vynth3v0Uwe_G8aZOtw/edit#heading=h.l39b6gu96vsv
     */
    if (!script_url_list) { return true }
    if (this.loading_scripts == true ) { return }

    this.loading_scripts = true
    this.status_loaded_scripts = false

    console.debug("Attempting to add", script_url_list)

    let insertion_node = null

    let existing_userscripts = this.discover_all_userscripts()
    let head = document.getElementsByTagName("head")[0]

    console.debug('existing_userscripts', existing_userscripts)

    if (existing_userscripts.length == 0){
      // If we don't have any existing scripts put at head
      insertion_node = head
    } else {
      // If we do, start insertion at end of last script
      insertion_node = existing_userscripts[existing_userscripts.length - 1]
    }

    if (!insertion_node) {
      throw "insertion_node is null"
    }

    for (let script_url_string of script_url_list){

      let does_script_exist = this.check_scripts_exist(script_url_string)
      if (does_script_exist == true) {
        continue    // prevent adding duplicate scripts
      }// this is here because we only want to adjust the insertion node based on this
      // prevents duplicates from user and from valid existing scripts

      if (typeof script_url_string != 'string') {
        console.log("Not a valid string")
        continue
      }

      let result = await this.add_script(
        script_url_string,
        insertion_node)

      // 2 We assume we will insert before any position we provide here
      insertion_node = insertion_node.nextSibling
      console.log(insertion_node)
    }

    this.status_loaded_scripts = true
    this.loading_scripts = false
  }

  private check_scripts_exist(id): any  {

    let result = document.getElementById(id)
    console.log(result)
    if (result) { return true }
    else {return false}
  }

  private add_script(
    script_url_string,
    insertion_node): any {


    let userscript_namespace_string = this.userscript_namespace_string    // promise will be different context

    return new Promise(function(resolve, reject) {

      let newScriptTag = document.createElement("script")
      newScriptTag.type = "text/javascript"
      newScriptTag.id = script_url_string
      newScriptTag.title = userscript_namespace_string

      // add to document
      // https://www.javascripttutorial.net/javascript-dom/javascript-insertafter/
      insertion_node.parentNode.insertBefore(newScriptTag, insertion_node.nextSibling)

      // add onload call back
      newScriptTag.onload = function () {
        console.log("added", script_url_string)
        resolve()
      }
      // error
      newScriptTag.onerror = function (error) {
        reject(error, newScriptTag)
      }
      // add script src
      newScriptTag.setAttribute('src', script_url_string)


    });

  }

  private get_line_number(stack): any {

    let starting_index = stack.search("anonymous");
    let ending_index = stack.search("at try_run");
    if (ending_index == -1) {
      ending_index = stack.search("at async try_run");
    }
    let offset = 10
    let start = starting_index + offset

    let line_and_char = stack.slice(start + 1, ending_index - 2)
    console.log(line_and_char)

    let line_and_char_list = line_and_char.split(":")
    let line = parseInt(line_and_char_list[0])
    let char = parseInt(line_and_char_list[1])

    let line_offset = -2
    let char_offset = 0 // not sure how to handle the child length thing

    line = line + line_offset
    char = char + char_offset
    //console.debug(line, char)

    return [line, char] 
  }
}
