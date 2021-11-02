// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })
import 'cypress-file-upload';
import {v4 as uuidv4} from 'uuid';
import testUser from '../fixtures/users.json'
import 'cypress-wait-until';
import labelsForAttributes from "../fixtures/labelsForAttributes.json";

Cypress.Commands.add('rightclickdowncanvas', function (x, y) {
  cy.document().then((doc) => {
    const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
    const real_x = x + canvas_client_box.x;
    const real_y = y + canvas_client_box.y;
    cy.get('#canvas_wrapper').then(($el) => {
      cy.wrap($el)
        .trigger('mouseover', {
          eventConstructor: 'MouseEvent',
          clientX: real_x,
          clientY: real_y,
          force: true
        })
        .trigger('mousemove', {
          eventConstructor: 'MouseEvent',
          clientX: real_x,
          clientY: real_y,
          force: true
        })
        .trigger('mouseover', {
          eventConstructor: 'MouseEvent',
          clientX: real_x,
          clientY: real_y,
          force: true
        })
        .trigger('contextmenu', {
          clientX: real_x,
          clientY: real_y,
          force: true
        })
    })
  })
})

Cypress.Commands.add('mousedowncanvas', function (x, y) {
  cy.document().then((doc) => {
    const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
    const real_x = x + canvas_client_box.left;
    const real_y = y + canvas_client_box.top;
    cy.get('#canvas_wrapper').then(($el) => {
      cy.wrap($el)
        .trigger('mousemove', {
          eventConstructor: 'MouseEvent',
          clientX: real_x,
          clientY: real_y,
          force: true
        })
        .trigger('mousedown', {
          button: 0,
          eventConstructor: 'MouseEvent',
          clientX: real_x,
          clientY: real_y,
          force: true
        })
    })
  })
})

Cypress.Commands.add('dragcanvas', function (from_x, from_y, to_x, to_y) {
  cy.document().then((doc) => {
    const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
    const real_from_x = from_x + canvas_client_box.x;
    const real_from_y = from_y + canvas_client_box.y;
    const real_to_x = to_x + canvas_client_box.x;
    const real_to_y = to_y + canvas_client_box.y;
    const movementX = real_to_x - real_from_x;
    const movementY = real_to_y - real_from_y;
    cy.get('#canvas_wrapper').then(($el) => {
      cy.wrap($el)
        .trigger('mouseover', {
          eventConstructor: 'MouseEvent',
          clientX: real_from_x,
          clientY: real_from_y,
          force: true
        })
        .trigger('mousemove', {
          eventConstructor: 'MouseEvent',
          clientX: real_from_x,
          clientY: real_from_y,
          force: true
        })
        .trigger('mousedown', {
          button: 0,
          eventConstructor: 'MouseEvent',
          clientX: real_from_x,
          clientY: real_from_y,
          force: true,
        })
        .trigger('mousemove', {
          eventConstructor: 'MouseEvent',
          clientX: real_to_x,
          clientY: real_to_y,
          force: true
        })
        .trigger('mousemove', {
          eventConstructor: 'MouseEvent',
          clientX: real_to_x,
          clientY: real_to_y,
          force: true
        })
        .trigger('mousemove', {
          eventConstructor: 'MouseEvent',
          clientX: real_to_x,
          clientY: real_to_y,
          force: true
        })
        .trigger('mouseup', {
          eventConstructor: 'MouseEvent',
          clientX: real_to_x,
          clientY: real_to_y,
          force: true
        })
    })
  })
})

Cypress.Commands.add('mouseovercanvas', function (x, y) {

  cy.document().then((doc) => {
    const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
    const real_x = x + canvas_client_box.x;
    const real_y = y + canvas_client_box.y;
    cy.get('#canvas_wrapper').then(($el) => {
      cy.wrap($el)
        .trigger('mouseover', {
          button: 0,
          eventConstructor: 'MouseEvent',
          clientX: real_x,
          clientY: real_y,
          force: true
        })
    })
  })

})

Cypress.Commands.add('mousemovecanvas', function (x, y) {

  cy.document().then((doc) => {
    const canvas_client_box = doc.getElementById('canvas_wrapper').getBoundingClientRect();
    const real_x = x + canvas_client_box.x;
    const real_y = y + canvas_client_box.y;
    cy.get('#canvas_wrapper').then(($el) => {
      cy.wrap($el)
        .trigger('mousemove', {
          button: 0,
          eventConstructor: 'MouseEvent',
          clientX: real_x,
          clientY: real_y,
          force: true
        })
    })
  })

})
Cypress.Commands.add('mouseupcanvas', function (x, y) {
  cy.get('#canvas_wrapper').then(($el) => {
    cy.wrap($el)
      .trigger('mouseup', {force: true})
  })
})
Cypress.Commands.add('registerDataPlatformTestUser', function () {

  cy.visit('http://localhost:8085/user/new', {timeout: 18000});
  cy.wait(5000);
  cy.get('[data-cy=email-input]').click({force: true});
  cy.get('[data-cy=email-input]').type(testUser.email);
  cy.get('[data-cy="create-user-button"] > .v-btn__content').click();
  cy.wait(500);
  // cy.get('[data-cy="error-email"]').should('not.be.visible');
  cy.wait(3500);
  cy.wait(2000);
  cy.url().should('eq', 'http://localhost:8085/user/builder/signup')
  cy.wait(2000)
  cy.get('[data-cy=first_name]').click();
  cy.get('[data-cy=first_name]').type('Diffgram');
  cy.get('[data-cy=last_name]').type('e2e');
  cy.get('[data-cy=how_hear_about_us]').type('Testing');
  cy.get('[data-cy=city]').type('Testing City');
  cy.get('[data-cy=role]').click()
  cy.get('.v-list.v-select-list div').contains('Other').click({force: true})
  cy.get('[data-cy=company]').click();
  cy.get('[data-cy=company]').type('Diffgram');
  cy.get('[data-cy=demo_select]').parent().click()
  cy.get('.v-list.v-select-list div').contains('Not yet.').click({force: true})
  cy.get('.v-slider__tick:nth-child(2)').click();
  cy.get('[data-cy=finish_singup_button]').click();
  cy.wait(1500);
  // Get Confirmation Link
  // Set Password
  cy.visit('http://localhost:8085/user/edit/');
  cy.get('.v-main__wrap').click();
  cy.get('[data-cy="set_password_button"] > .v-btn__content').click();
  cy.get('[data-cy=password1]').click();
  cy.get('[data-cy=password1]').type('diffgram123');
  cy.get('[data-cy=password2]').click();
  cy.get('[data-cy=password2]').type('diffgram123');
  cy.get('[data-cy="save_password_button"] > .v-btn__content').click();
  cy.wait(3000);
  // Create test Project
  cy.visit('http://localhost:8085/a/project/new');
  cy.get('.v-card:nth-child(2)').click();
  cy.get('[data-cy=project_name]').click();
  for (let i = 0; i < 40; i++) {
    cy.get('[data-cy=project_name]').type('{backspace}');
  }
  cy.get('[data-cy=project_name]').type('Diffgram Testing E2E');
  cy.get('[data-cy=project_goal]').type('For e2e testing');
  cy.get('[data-cy="create_project_button"] > .v-btn__content').click();
})


Cypress.Commands.add('signupPro', function () {
    cy.visit('http://localhost:8085/user/pro/signup');
    // This part is not quite working yet

    cy.get('[data-cy=occupation_list]').click({force: true})
    let occupation_name_search = "engineer"
    cy.get('[data-cy=occupation_list]').type(occupation_name_search)
    cy.wait(100)
    let occupation_name_contains = 'Ship'
    cy.get('.v-list.v-select-list div').contains(occupation_name_contains).click({force: true})

    cy.get('[data-cy=first_name]').click({force: true});
    cy.get('[data-cy=first_name]').type('pro');
    cy.get('[data-cy=last_name]').type('e2e');
    cy.get('[data-cy=linkedin_profile_url]').type('linkedin_profile_url yes');
    cy.get('[data-cy=how_hear_about_us]').type('Testing');
    cy.get('[data-cy=city]').type('Testing City');

    cy.get('[data-cy=role]').click()
    cy.wait(50)
    cy.get('.v-list-item div').contains('Student').click({force: true})

    cy.get('[data-cy=finish_sign_up_button]').click();
    cy.wait(1500);

  })

Cypress.Commands.add('registerProTestUser', function () {

  cy.visit('http://localhost:8085/user/pro/new');
  cy.wait(5000);
  cy.get('[data-cy=email-input]', {timeout: 20000}).click({force: true});
  cy.get('[data-cy=email-input]').type(testUser.email);
  cy.get('[data-cy="create-user-button"] > .v-btn__content').click();
  cy.wait(500);
  cy.get('[data-cy="error-email"]').should('not.be.visible');
  cy.wait(1500);

  cy.url().should('eq', 'http://localhost:8085/user/pro/signup')
  cy.wait(2000)

  cy.signupPro()

  // Get Confirmation Link
  cy.request('GET', `http://localhost:8085/api/user/confirmation-token?email=${testUser.email}`)
    .then((response) => {
      // response.body is automatically serialized into JSON
      cy.visit(`http://localhost:8085/user/account/verify_email/${testUser.email}/${response.body.token}`);
      cy.wait(3000);
      // Set Password
      cy.visit('http://localhost:8085/user/edit/');
      cy.get('.v-main__wrap').click();
      cy.get('[data-cy="set_password_button"] > .v-btn__content').click();
      cy.get('[data-cy=password1]').click();
      cy.get('[data-cy=password1]').type('diffgram123');
      cy.get('[data-cy=password2]').click();
      cy.get('[data-cy=password2]').type('diffgram123');
      cy.get('[data-cy="save_password_button"] > .v-btn__content').click();
      cy.wait(3000);
    })
})


Cypress.Commands.add('loginByForm', function (email, password) {
  Cypress.log({
    name: 'loginByForm',
    message: `${email} | ${password}`,
  })
  cy.visit('http://localhost:8085/user/login')
  let LOCAL_STORAGE_MEMORY = {};

  const getInitialStore = () => cy.window().its('app.$store')

  getInitialStore().its('state.user.logged_in').then((user_logged_in) => {

    if (user_logged_in == false) {
      cy.wait(10000);
      cy.get('[data-cy=email]')
        .type(email)
        .should('have.value', email)
      cy.get('[data-cy=password]')
        .type(password)
        .should('have.value', password)
      cy.get('[data-cy=login]').click();
      cy.wait(3000);
      Object.keys(LOCAL_STORAGE_MEMORY).forEach(key => {
        localStorage.setItem(key, LOCAL_STORAGE_MEMORY[key]);
      });
      const getStore = () => cy.window().its('app.$store')
      getStore().its('state.user.logged_in').should('eq', true);
    }

  })
});

Cypress.Commands.add('gotToProject', function (project_string_id) {
  cy.visit('http://localhost:8085/projects')
  cy.wait(5000);
  cy.get(`[data-cy="project-title-${project_string_id}"] > div`).click({force: true});
  cy.wait(1500);
});

Cypress.Commands.add('goToSchemaFromToolbar', function () {
  cy.wait(3000);
  cy.get('#open_main_menu > .v-btn__content').click({force: true});
  cy.get('[data-cy=main_menu_labels]').click({force:true})
  cy.wait(2000)
});

Cypress.Commands.add('goToStudioFromToolbar', function () {
  cy.get('#open_main_menu > .v-btn__content').click({force: true});
  cy.get('[data-cy="main_menu_data_explorer"]').click({force: true});
  cy.wait(5000);
  cy.get('[data-cy="minimize-file-explorer-button"] > .v-btn__content').click({force: true});
});

Cypress.Commands.add('createAndSelectNewAttributeGroup', function () {
  cy.get(`[data-cy=new_attribute_button]`).click({force: true});
  cy.get(`[data-cy="attribute_group_header_Untitled Attribute Group"]`).first().click({force: true});
});

Cypress.Commands.add('selectLabel', function (name, alternate_selector = 'label_select_attribute') {
  cy.wait(2000) // assumes will need to load
  cy.get(`[data-cy=${alternate_selector}]`).click({force: true});
  cy.wait(300)
  cy.get('.v-menu__content .v-list.v-select-list .v-list-item span span').contains(
    name).first().click({force: true})
});

Cypress.Commands.add('createAttributeOptions', function (option_list) {
  cy.get('[data-cy=new_attribute_option_button]').click({force: true});

  cy.wait(400);
  for(let option of option_list){
    cy.get('[data-cy=attribute_option_name]').click({force: true});
    cy.wait(750)
    cy.get('[data-cy=attribute_option_name]').type(option, {force: true});
    cy.wait(300)
    cy.get('[data-cy="create_attribute_option"] > .v-btn__content').click({force: true});

  }
  cy.get('[data-cy="close_button_new_attribute"]').click({force: true});
});

Cypress.Commands.add('typesAttributePrompt', function (name) {
  cy.get('[data-cy=attribute_prompt]').click({force: true});
  cy.get('[data-cy=attribute_prompt]').type(name);
});

Cypress.Commands.add('typesInternalTagPrompt', function (name) {
  cy.get('[data-cy=attribute_tag]').click({force: true});
  cy.get('[data-cy=attribute_tag]').type(selectAttribute.tag);
});



Cypress.Commands.add('createLabels', function (labels_list) {
  cy.visit('http://localhost:8085/project/diffgram-testing-e2e/labels')
  cy.wait(2500)
  const label_list_obj = labels_list.map(elm => ({...elm, exists: false}))
  cy.request({
    method: 'GET',
    url: `localhost:8085/api/project/diffgram-testing-e2e/labels/refresh`,
    failOnStatusCode: false
  }).then((response) =>{
    cy.log('RESPONSE')
    cy.log(response)
    response.body.labels_out.forEach((label_response_obj) => {
      const label_obj = label_list_obj.find(elm => elm.name === label_response_obj.label.name)
      if(label_obj){
        label_obj.exists = true;
      }
    })
    cy.get('[data-cy=new_label_template]').first().click({force: true});
    for (let i = 0; i < label_list_obj.length; i++) {
      if(label_list_obj[i].exists){
        continue
      }
      cy.get('[data-cy=label_name_text_field]').click({force: true});
      cy.get('[data-cy=label_name_text_field]').type(label_list_obj[i].name);
      cy.get('[data-cy=create_label_button]').click({force: true});
      cy.wait(1500)
    }

  })

});

Cypress.Commands.add('uploadImageWithLabels', function (project_string_id) {
  cy.visit(`http://localhost:8085/studio/upload/${project_string_id}`);
  cy.get('[data-cy=start_upload_wizard]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=upload_new_data]').click({force: true});
  cy.wait(1200);
  cy.get('[data-cy=set_dataset_button]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=from_local_button]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=with_pre_labels_button]').click({force: true});
  const fileFixture = {
    filePath: './test-images/testimage2.jpg',
    fileName: `testimage2.jpg`,
  }
  const labelsFixture = {
    filePath: './testDiffgramUpload.json',
    fileName: `testDiffgramUpload.json`,
  }
  cy.get('.dz-hidden-input').attachFile(fileFixture)
  cy.get('.dz-hidden-input').attachFile(labelsFixture)

  cy.wait(1000);
  cy.get('[data-cy=continue_upload_step]').click();
  cy.wait(500);
  cy.get('[data-cy=continue_file_mapping]').click({force: true})
  // Mapping Process
  cy.wait(700);
  cy.get('[data-cy=select_instance_type]').click({force: true})
  cy.get('.v-list-item__title').contains('type').first().click({force: true})
  cy.wait(500)
  cy.get('[data-cy=continue_file_mapping]').click({force: true})
  cy.wait(700);
  cy.get('[data-cy=select_label_name]').click({force: true})
  cy.get('.v-list-item__title').contains('name').first().click({force: true})
  cy.wait(500)
  cy.get('[data-cy=continue_file_mapping]').click({force: true})
  cy.wait(700);
  cy.get('[data-cy=select_file_name]').click({force: true})
  cy.get('.v-list-item__title').contains('myFileName').first().click({force: true})
  cy.wait(500)
  cy.get('[data-cy=continue_file_mapping]').click({force: true})
  cy.wait(700);
  cy.get('[data-cy=use_model_button]').click({force: true})
  cy.wait(700);
  cy.get('[data-cy=select_model_id]').click({force: true})
  cy.get('.v-list-item__title').contains('model_id').first().click({force: true})
  cy.wait(500)
  cy.get('[data-cy=continue_file_mapping]').click({force: true})
  cy.wait(700);
  cy.get('[data-cy=select_model_run_id]').click({force: true})

  cy.get('.v-list-item__title').contains('run_id').first().click({force: true})
  cy.wait(500)
  cy.get('[data-cy=continue_file_mapping]').click({force: true})
  cy.wait(700);
  cy.get('[data-cy=yes_metadata_button]').click({force: true})
  cy.wait(700);
  cy.get('[data-cy=select_metadata]').click({force: true})
  cy.get('.v-menu__content:visible .v-list-item__title').contains('metatada').eq(0).click({force: true})
  cy.wait(500)
  cy.get('[data-cy=continue_file_mapping]').click({force: true})
  cy.wait(500)
  cy.get('[data-cy=select_x_min]').first().click({force: true})
  cy.get('.v-menu__content:visible .v-list-item__title').contains('lower_x').eq(0).click({force: true})
  cy.wait(500)
  cy.get('[data-cy=select_x_max]').first().click({force: true})
  cy.get('.v-menu__content:visible .v-list-item__title').contains('upper_x').eq(0).click({force: true})
  cy.wait(500)
  cy.get('[data-cy=select_y_min]').first().click({force: true})
  cy.get('.v-menu__content:visible .v-list-item__title').contains('lower_y').eq(0).click({force: true})
  cy.wait(500)
  cy.get('[data-cy=select_y_max]').first().click({force: true})
  cy.get('.v-menu__content:visible .v-list-item__title').contains('upper_y').eq(0).click({force: true})
  cy.wait(500)
  cy.get('[data-cy=continue_instance_mapping]').click({force:true})
  cy.wait(700);
  cy.get('[data-cy=start_files_upload_button]').click();
  cy.wait(3000);
  cy.get('[data-cy=close_wizard_button]').click();
  cy.wait(3000);
  cy.get('[data-cy=refresh-input-icon]').click();
  cy.wait(3000);
  cy.get('[data-cy=input-table] tbody tr').first().get('.file-link').first().click({force: true});

});
Cypress.Commands.add('uploadAndViewSampleImage', function (project_string_id) {
  cy.visit(`http://localhost:8085/studio/upload/${project_string_id}`);
  cy.get('[data-cy=start_upload_wizard]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=upload_new_data]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=set_dataset_button]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=from_local_button]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=with_no_pre_labels_button]').click({force: true});
  const fileFixture = {
    filePath: './test-images/testimage1.jpg',
    fileName: `my-file-${uuidv4().toString()}.jpg`,
  }
  cy.get('.dz-hidden-input').attachFile(fileFixture)

  cy.wait(1000);
  cy.get('[data-cy=continue_upload_step]').click();
  cy.wait(700);
  cy.get('[data-cy=start_files_upload_button]').click();
  cy.wait(3000);
  cy.get('[data-cy=close_wizard_button]').click();
  cy.wait(3000);
  cy.get('[data-cy=refresh-input-icon]').click();
  cy.wait(3000);
  cy.get('[data-cy=input-table] tbody tr').first().get('.file-link').first().click({force: true});

});

Cypress.Commands.add('uploadAndViewSampleVideo', function (project_string_id) {
  cy.visit(`http://localhost:8085/studio/upload/${project_string_id}`)
  cy.get('[data-cy=start_upload_wizard]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=upload_new_data]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=set_dataset_button]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=from_local_button]').click({force: true});
  cy.wait(700);
  cy.get('[data-cy=with_no_pre_labels_button]').click({force: true});
  cy.fixture('./test-videos/challenge_videoTrim_re_saved.mp4', 'binary')
    .then(Cypress.Blob.binaryStringToBlob)
    .then(fileContent => {
        cy.get('.dz-hidden-input').attachFile({
          fileContent,
          fileName: `my-file-${uuidv4().toString()}.mp4`,
          mimeType: 'video/mp4',
          encoding: 'utf8'
        })
      }
    );


  cy.get('[data-cy=continue_upload_step]').click();
  cy.wait(700);
  cy.get('[data-cy=start_files_upload_button]').click();
  cy.wait(8000);
  cy.get('[data-cy=close_wizard_button]').click();
  cy.wait(10000);
  cy.get('[data-cy=refresh-input-icon]').click();
  cy.wait(3000);
  cy.get('[data-cy=input-table] tbody tr').first().get('.file-link').first().click({force: true});

});


Cypress.Commands.add('createInstanceTemplate', function (name, instance_data) {
  cy.visit('http://localhost:8085/project/diffgram-testing-e2e/labels')
  cy.wait(500)
  cy.get('[data-cy=new_instance_template]').first().click({force: true});
  cy.get('[data-cy=instance_template_name_text_field]').type(name);
  cy.wait(500)
  for(let node of instance_data.nodes){
    cy.mousedowncanvas(node.x, node.y)
    cy.wait(500)
    cy.mouseupcanvas(node.x, node.y)
  }
  for(let edge of instance_data.edges){
    cy.mousemovecanvas(instance_data.nodes[edge[0]].x, instance_data.nodes[edge[0]].y)
    cy.mousedowncanvas(instance_data.nodes[edge[0]].x, instance_data.nodes[edge[0]].y)
    cy.wait(500)
    cy.mouseupcanvas(instance_data.nodes[edge[0]].x, instance_data.nodes[edge[0]].y)

    cy.mousemovecanvas(instance_data.nodes[edge[1]].x, instance_data.nodes[edge[1]].y)
    cy.mousedowncanvas(instance_data.nodes[edge[1]].x, instance_data.nodes[edge[1]].y)
    cy.wait(500)
    cy.mouseupcanvas(instance_data.nodes[edge[1]].x, instance_data.nodes[edge[1]].y)
  }

});


Cypress.Commands.add('select_label', function (label_name) {
  // hook for future
  if(!label_name){
    return
  }
  cy.get('[data-cy=label_select]').click({force: true})
  cy.get('.v-list-item.v-list-item--link').not(':contains("attributes")').contains(label_name).click({force: true})
});


