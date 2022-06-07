import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";

describe('Annotation Text Interface display', () => {

  context('Text Interface display', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)

    })

    it('Displays a Text file', () => {
      cy.upload_text_file(testUser.project_string_id);
      cy.get('[data-cy="token_1_line_1"]').should('be.visible');
      cy.wait(200)
      cy.get('[data-cy="token_1_line_1"]').click()
    //   cy.get('[data-cy="sidebar-left-container"]').should('be.visible');
    //   cy.get('[data-cy="secondary_3d_canvas_container"]').should('be.visible');
    })

    // it('Displays Mini Cameras for 3D Scene', () =>{
    //   cy.get('[data-cy="x_axis_3d_canvas"]').should('be.visible');
    //   cy.get('[data-cy="y_axis_3d_canvas"]').should('be.visible');
    //   cy.get('[data-cy="z_axis_3d_canvas"]').should('be.visible');
    // })


    // it('Displays the toolbar on the 3D Interface', () => {
    //   cy.get('[data-cy="toolbar_sensor_fusion"]').should('be.visible');
    //   cy.get('[data-cy="toolbar_label_selector"]').should('be.visible');
    //   cy.get('[data-cy="instance-type-select"]').should('be.visible');
    //   cy.get('[data-cy="save_button"]').should('be.visible');
    //   cy.get('[data-cy="previous_file_button"]').should('be.visible');
    //   cy.get('[data-cy="next_file_button"]').should('be.visible');
    //   cy.get('[data-cy="refresh_instances"]').should('be.visible');
    //   cy.get('[data-cy="display_hotkeys_button"]').should('be.visible');
    //   cy.get('[data-cy="more_button"]').should('be.visible');
    // })

    // it('Displays the instance list detail on the left panel', () => {
    //   cy.get('[data-cy="instance_detail_list"]').should('be.visible');

    // })
  })
})
