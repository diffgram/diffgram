import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';


describe('Annotate Files Tests', () => {

  context('Explore Dataset', () => {
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

    context('It Can write a query and filter files', () => {
      it('Correctly opens the context menu on a Bounding Box', () => {
        cy.wait(2000)
        cy.get('[data-cy="minimize-file-explorer-button"]').click({force: true})
        cy.wait(1000)
        cy.select_label('apple')
        cy.wait(3000)
        const boxes = [[75,75,120,120], [95,95,180,180], [150,150,215,215]]
        for(const box of boxes){
          cy.mousedowncanvas(box[0], box[1]);
          cy.wait(500)
          cy.mouseupcanvas();
          cy.wait(1000)
          cy.mousedowncanvas(box[2], box[3]);
          cy.wait(500)
          cy.mouseupcanvas();
          cy.wait(2000)
        }
        cy.get('[data-cy="file_explorer_button"]').click({force: true});
        cy.get('[data-cy="tab__Dataset Explorer"]').click({force: true});
        cy.wait(500)
        cy.get('[data-cy=query_input_field]').clear()
        cy.wait(500)
        cy.get('[data-cy=query_input_field]').type('labels.apple > 1 {enter}')
        cy.wait(500)
        cy.get('[data-cy=query_input_field]').blur()
        cy.wait(1000);
        cy.get('[data-cy=query_input_field]').focus();
        cy.wait(1000);
        cy.get('[data-cy=execute_query_button]').click({force: true});

        cy.wait(2500);
        cy.get('.file-preview').its('length').should('be.gte', 1)
      })
    })

  })

})
