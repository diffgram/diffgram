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
    let url_launch = '/api/v1/job/launch'
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
      cy.get('[data-cy="label_schema_selector"]').should('be.visible')
      cy.get('[data-cy="step-labels-title"]').should('be.visible')
      cy.get('[data-cy="manage-labels-button"]').should('be.visible')
    })

    it('Correctly Selects Schema and go to next step', () => {
      cy.intercept(url).as('update_job')
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
      cy.intercept(url).as('update_job')
      cy.get('[data-cy="member-select"]').click({force: true})
      cy.get('.v-list-item.v-list-item--link').contains(testUser.first_name + ' ' + testUser.last_name).click({force: true})
      cy.get('.v-list-item.v-list-item--link').contains(testUser.first_name + ' ' + testUser.last_name).click({force: true})
      cy.get('[data-cy="task-template-users-step"] [data-cy="wizard_navigation_next"]').click({force: true});
      cy.wait('@update_job').its('response').should('have.property', 'statusCode', 200)
    })

    it('Correctly Shows Reviewers Step in Wizard', () => {
      cy.get('[data-cy="task-template-reviewer-step"]').should('be.visible')
      cy.get('[data-cy="task-template-reviewer-step-title"]').should('be.visible')
      cy.get('[data-cy="task-template-reviewer-radio-yes"]').should('exist')
      cy.get('[data-cy="task-template-reviewer-radio-no"]').should('exist')
    })

    it('Correctly sets reviews to 100%', () => {
      cy.intercept(url).as('update_job')
      cy.get('[data-cy="task-template-reviewer-radio-yes"]').click({force: true})
      cy.get('[data-cy="task-template-reviewer-review-all"]').click({force: true})
      cy.get('[data-cy="task-template-reviewer-step"] [data-cy="wizard_navigation_next"]').click({force: true});
      cy.wait('@update_job').its('response').should('have.property', 'statusCode', 200)
    })

    it('Correctly Shows Dataset Attachment Step', () => {
      cy.get('[data-cy="task-template-dataset-step"]').should('be.visible')
      cy.get('[data-cy="task-template-dataset-step-title"]').should('be.visible')
      cy.get('[data-cy="mxgraphcontainer"]').should('be.visible')
      cy.get('[data-cy="job-file-routing"]').should('be.visible')
      cy.get('[data-cy="directory-selector"]').should('be.visible')
      cy.get('[data-cy="job-output-dir-selector"]').should('be.visible')
    })

    it('Correctly Attaches a dataset and goes to next step', () => {
      cy.intercept(url).as('update_job')
      cy.get('[data-cy="directory_select"]').first().click({force: true});
      cy.get('.v-menu__content .v-list .v-list-item').contains(' Default').click({force: true})

      cy.get('[data-cy="task-template-dataset-step"] [data-cy="wizard_navigation_next"]').click({force: true});
      cy.wait('@update_job').its('response').should('have.property', 'statusCode', 200)


    })



    it('Correctly Goes from Advanced Options to Credentials Step', () => {
      cy.get('[data-cy="task-template-credentials-step"]').should('be.visible')
      .get('[data-cy="credentials-step-title"]').should('be.visible')
      .get('[data-cy="open-create-credential"]').should('be.visible')
      .get('[data-cy="open-create-credential"]').click({force: true})
      .get('[data-cy="create-credential-button"]').click({force: true})
      .get('[data-cy="refresh-credentials"]').click({force: true})
      .get('[data-cy="credential-checkbox-0"]').click({force: true})
      .get('[data-cy="requires-button"]').should('be.visible')
      .get('[data-cy="clear-button"]').should('be.visible')
      .get('[data-cy="requires-button"]').click({force: true})

      .intercept(url_launch).as('launch_job')
      .get('[data-cy="task-template-credentials-step"] [data-cy="wizard_navigation_next"]').click({force: true})
      .wait('@launch_job').its('response').should('have.property', 'statusCode', 200)

    })



  })

})
