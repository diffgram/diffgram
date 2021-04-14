import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';


describe('Annotate Files Tests', () => {

  context('Test Annotate files Advanced Settings', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      // login before all tests
      cy.loginByForm(testUser.email, testUser.password);
      cy.gotToProject(testUser.project_string_id);
      cy.createLabels(testLabels)
      cy.uploadAndViewSampleImage(testUser.project_string_id);

    })

    context('Advanced Annotation Settings Menu', () => {

      it('Displays the Advanced Settings Option', () => {
        cy.get('[data-cy=advanced_setting]').click({force: true})
        cy.get('[data-cy=annotation_setting_menu]').should('be.visible')
      })

      it('Toggles Show Any Text',() => {
        // Draw 2 Boxes
        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.mousedowncanvas(75, 75);
        cy.mouseupcanvas();
        cy.mousedowncanvas(120, 120);
        cy.mouseupcanvas();

        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.mousedowncanvas(160, 160);
        cy.mouseupcanvas();
        cy.mousedowncanvas(200, 200);
        cy.mouseupcanvas();

        cy.wait(500)
        cy.get('[data-cy=advanced_setting]').click({force: true})
        cy.get('[data-cy=show_any_text_checkbox]').click({force: true})


        cy.wait(500)
      })

      it('Toggles Show Label Text',() => {
        // Draw 2 Boxes
        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.mousedowncanvas(75, 75);
        cy.mouseupcanvas();
        cy.mousedowncanvas(120, 120);
        cy.mouseupcanvas();

        cy.get(`[data-cy="${testLabels[0].name}"]`).first().click({force: true})
        cy.mousedowncanvas(160, 160);
        cy.mouseupcanvas();
        cy.mousedowncanvas(200, 200);
        cy.mouseupcanvas();

        cy.wait(500)
        cy.get('[data-cy=advanced_setting]').click({force: true})
        cy.get('[data-cy=show_any_text_checkbox]').click({force: true})


        cy.wait(500)
      })

    })

  })

})
