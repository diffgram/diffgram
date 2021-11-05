import testUser from '../../../fixtures/users.json';

describe('tasks_detail_pagination', () => {

  context('something', () => {
    before(function () {

      cy.createSampleTasksUsingBackend()

      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      cy.loginByForm(testUser.email, testUser.password);
      
    })

    it('Views job', () => {

      cy.visit(`http://localhost:8085/job/list`);
      cy.get('[data-cy="view_button"]').first().click({force: true})
      cy.wait(1000)

    })

    it('Goes to next page', () => {

      cy.get('[data-cy="task_list_next_page"]').first().click({force: true})
      cy.wait(3000)
      cy.get('[data-cy="task_status_icons"]').first().its('length').should('be.gte', 1)

    })

    it('Goes to previous page', () => {

      cy.get('[data-cy="task_list_previous_page"]').first().click({force: true})
      cy.wait(3000)
      cy.get('[data-cy="task_status_icons"]').first().its('length').should('be.gte', 1)

    })

  })

})
