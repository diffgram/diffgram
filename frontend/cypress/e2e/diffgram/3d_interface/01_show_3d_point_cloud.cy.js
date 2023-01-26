import testUser from '../../../fixtures/users.json';
import testLabels from "../../../fixtures/labels.json";

describe('Annotation 3D Interface display', () => {

  context('3D Interface display', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels)

    })

    it('Displays a 3D file', () => {
      cy.upload_3d_file(testUser.project_string_id)
      .wait(3000)
      .get('[data-cy="3d-editor-container"]').should('be.visible')
      .get('[data-cy="sidebar-left-container"]').should('be.visible')
      .get('[data-cy="secondary_3d_canvas_container"]').should('be.visible')
      .get('[data-cy="minimize-file-explorer-button"]').click({force: true})


    })

    it('Displays Mini Cameras for 3D Scene', () =>{
      cy.get('[data-cy="x_axis_3d_canvas"]').should('be.visible');
      cy.get('[data-cy="y_axis_3d_canvas"]').should('be.visible');
      cy.get('[data-cy="z_axis_3d_canvas"]').should('be.visible');
    })


    it('Displays the toolbar on the 3D Interface', () => {
      cy.get('[data-cy="toolbar_sensor_fusion"]').should('be.visible');
      cy.get('[data-cy="toolbar_label_selector"]').should('be.visible');
      cy.get('[data-cy="instance-type-select"]').should('be.visible');
      cy.get('[data-cy="save_button"]').should('be.visible');
      cy.get('[data-cy="previous_file_button"]').should('be.visible');
      cy.get('[data-cy="next_file_button"]').should('be.visible');
      cy.get('[data-cy="refresh_instances"]').should('be.visible');
      cy.get('[data-cy="display_hotkeys_button"]').should('be.visible');
      cy.get('[data-cy="more_button"]').should('be.visible');
    })

    it('Displays the instance list detail on the left panel', () => {
      cy.get('[data-cy="instance_detail_list"]').should('be.visible');

    })
  })
})
