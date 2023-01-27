import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';


describe('Annotate Files Tests', () => {

  context('Test Annotate files Advanced Settings', () => {
    before(function () {
      Cypress.Cookies.debug(true, {verbose: true})

      // login before all tests
      cy.loginByForm(testUser.email, testUser.password)
        .gotToProject(testUser.project_string_id)
        .createLabels(testLabels)
        .uploadAndViewSampleImage(testUser.project_string_id)

    })

    context('Advanced Annotation Settings Menu', () => {

      it('Displays the Advanced Settings Option', () => {
        cy.get('[data-cy=more_button]').click({force: true})
        .get('[data-cy=advanced_setting]').click({force: true})
      })

      it('Toggles Show Any Text',() => {
        // Draw 2 Boxes
        cy.select_label()
        cy.mousedowncanvas(75, 75);
        cy.mouseupcanvas();
        cy.mousedowncanvas(120, 120);
        cy.mouseupcanvas();

        cy.select_label()
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
        cy.select_label()
        cy.mousedowncanvas(75, 75);
        cy.mouseupcanvas();
        cy.mousedowncanvas(120, 120);
        cy.mouseupcanvas();

        cy.select_label()
        cy.mousedowncanvas(160, 160);
        cy.mouseupcanvas();
        cy.mousedowncanvas(200, 200);
        cy.mouseupcanvas();

        cy.wait(500)
        cy.get('[data-cy=more_button]').click({force: true});
        cy.get('[data-cy=advanced_setting]').click({force: true})
        cy.get('[data-cy=show_any_text_checkbox]').click({force: true})


        cy.wait(500)
      })

    })

  })

})
