import testUser from '../../../fixtures/users.json';

describe('tasks_detail_pagination', () => {

  context('tasks_detail_pagination', () => {
    before(function () {

      cy.createSampleTasksUsingBackend(10)

      Cypress.Cookies.debug(true, {verbose: true})
      Cypress.Cookies.defaults({
        preserve: ['session']
      })
      cy.loginByForm(testUser.email, testUser.password);
      
    })

    it('Views job', () => {

      cy.visit(`http://localhost:8085/job/list`);
      cy.get('[data-cy="view_button"]').first().click({force: true})
      cy.wait(3000)

    })

    it('Limits results', () => {

      cy.wait(5000)
      cy.get('[data-cy="task_list_filters"]').click({force: true})
      cy.get('[data-cy="task_list_per_page_limit_selector"]').first().click({force: true})    
      cy.get('.v-list.v-select-list div').contains('5').first().click({force: true})
      cy.get('[data-cy="task_list_refresh_task_list"]').click({force: true})
      cy.get('[data-cy="task_list_close_filters"]').click({force: true})
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
