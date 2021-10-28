import testUser from '../../../fixtures/users.json';
import testLabels from '../../../fixtures/labels.json';
import labelsForAttributes from "../../../fixtures/labelsForAttributes.json";


describe('Task Template Creation', () => {

  context('It creates a task template with the wizard', () => {
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
    let url = '/api/v1/project/*/job/update'
    it('Correctly Shows the First Step In the wizard', () => {
      cy.visit(`http://localhost:8085/project/${testUser.project_string_id}/job/new`);
      cy.get('[data-cy="wizard-title"]').should('be.visible')
      cy.get('[data-cy="task-template-name-input"]').should('be.visible')
      cy.get('[data-cy="wizard-name-subtitle"]').should('be.visible')

    })

    it('Correctly edits name and jumps to next step', () => {

      cy.intercept(url).as('update_job')
      cy.get('[data-cy="task-template-name-input"]').type(' +test-e2e')
      cy.get('[data-cy="task-template-step-name"] [data-cy="wizard_navigation_next"]').click();
      cy.wait('@update_job').its('response').should('have.property', 'statusCode', 200)
    })

    it('Correctly Shows Label Step in Wizard', () => {
      cy.get('[data-cy="label-select"]').should('be.visible')
      cy.get('[data-cy="step-labels-title"]').should('be.visible')
      cy.get('[data-cy="manage-labels-button"]').should('be.visible')
      cy.get('[data-cy="select-all-labels"]')
        .parent()
        .find('.v-input--selection-controls__ripple')
        .should('be.visible')
    })

    it('Correctly Edits Labels and go to next step', () => {
      cy.intercept(url).as('update_job')
      cy.get('[data-cy="select-all-labels"]')
        .click({force: true});
      cy.selectLabel(testLabels[0].name, 'label-select')
        cy.get('[data-cy="step-labels-title"]').should('be.visible')
        .get('[data-cy="manage-labels-button"]').should('be.visible')

      cy.get('[data-cy="task-template-labels-step"] [data-cy="wizard_navigation_next"]').click();
      cy.wait('@update_job').its('response').should('have.property', 'statusCode', 200)
    })

    it('Correctly Shows Users Step in Wizard', () => {
      cy.get('[data-cy="task-template-users-step"]').should('be.visible')
      cy.get('[data-cy="task-template-users-step-title"]').should('be.visible')
      cy.get('[data-cy="task-template-users-step-subtitle"]').should('be.visible')
      cy.get('[data-cy="member-select"]').should('be.visible')

    })

    it('Correctly Selects a User and goes to next step', () => {
      cy.get('[data-cy="member-select"]').click({force: true})
      cy.get('[data-cy="member-select__select-all"]').click({force: true})
      cy.get('.v-list-item.v-list-item--link').contains(testUser.first_name + ' ' + testUser.last_name).click({force: true})

    })
  })

})
